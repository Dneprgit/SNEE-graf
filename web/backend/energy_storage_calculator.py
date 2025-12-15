"""
Модуль расчета диспетчерского графика работы СНЭЭ
Портирован с VBA алгоритма water-filling и квадратичной оптимизации (QP)
"""
import numpy as np
from typing import List, Tuple, Dict
from scipy.optimize import minimize, LinearConstraint, Bounds


class EnergyStorageCalculator:
    """Класс для расчета оптимального графика работы СНЭЭ"""
    
    HOURS = 24
    
    def __init__(self, rated_power_mw: float, rated_capacity_mwh: float, efficiency: float):
        """
        Инициализация калькулятора СНЭЭ
        
        Args:
            rated_power_mw: Мощность инвертора в МВт
            rated_capacity_mwh: Емкость батареи в МВтч
            efficiency: КПД цикла (0-1)
        """
        if rated_power_mw <= 0 or rated_capacity_mwh <= 0:
            raise ValueError("Мощность и емкость должны быть положительными")
        if efficiency <= 0 or efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне (0, 1]")
            
        self.rated_power = rated_power_mw
        self.rated_capacity = rated_capacity_mwh
        self.efficiency = efficiency
        self.half_cycle_efficiency = np.sqrt(efficiency)  # КПД полуцикла
        
    def calculate_dispatch_schedule(self, load_profile: List[float]) -> np.ndarray:
        """
        Расчет диспетчерского графика СНЭЭ
        
        Args:
            load_profile: Суточный профиль баланса мощности (24 часа)
                         + избыток, - дефицит
        
        Returns:
            Массив мощности СНЭЭ на шинах (24 часа)
            + разряд (выдача в сеть), - заряд (потребление из сети)
        """
        if len(load_profile) != self.HOURS:
            raise ValueError(f"Профиль должен содержать {self.HOURS} значений")
            
        load = np.array(load_profile, dtype=float)
        eess_load = np.zeros(self.HOURS)
        
        # 1. Расчет почасовых лимитов заряда и разряда
        max_charge_internal = np.minimum(
            np.maximum(load, 0),
            self.rated_power
        ) * self.half_cycle_efficiency
        
        max_discharge_internal = np.minimum(
            np.maximum(-load, 0) / self.half_cycle_efficiency,
            self.rated_power
        )
        
        sum_charge = np.sum(max_charge_internal)
        sum_discharge = np.sum(max_discharge_internal)
        
        # 2. Определение используемой энергии
        used_capacity = min(sum_charge, sum_discharge, self.rated_capacity)
        
        if used_capacity <= 0:
            return eess_load
            
        # 3. Определение уровня для заряда (water-filling)
        ub_charge = load.copy()
        lb_charge = ub_charge - (max_charge_internal / self.half_cycle_efficiency)
        charge_level = self._get_level_bounded(
            lb_charge, ub_charge, -1, used_capacity / self.half_cycle_efficiency
        )
        
        # 4. Определение уровня для разряда (water-filling)
        lb_discharge = load.copy()
        ub_discharge = lb_discharge + (max_discharge_internal * self.half_cycle_efficiency)
        discharge_level = self._get_level_bounded(
            lb_discharge, ub_discharge, 1, used_capacity * self.half_cycle_efficiency
        )
        
        # 5. Расчет почасового графика мощности
        balance = 0.0
        
        for i in range(self.HOURS):
            charge = min(
                max_charge_internal[i],
                max(load[i] - charge_level, 0) * self.half_cycle_efficiency
            )
            
            discharge = min(
                max_discharge_internal[i],
                max(discharge_level - load[i], 0) / self.half_cycle_efficiency
            )
            
            net_internal = discharge - charge
            balance += net_internal
            
            if net_internal > 0:
                # Разряд: выдаем в сеть с учетом потерь
                eess_load[i] = net_internal * self.half_cycle_efficiency
            elif net_internal < 0:
                # Заряд: забираем из сети с учетом потерь
                eess_load[i] = net_internal / self.half_cycle_efficiency
            else:
                eess_load[i] = 0.0
                
        return eess_load
    
    def _get_level_bounded(self, lb: np.ndarray, ub: np.ndarray, 
                          dir_factor: int, area: float) -> float:
        """
        Water-filling алгоритм для определения уровня заряда/разряда
        
        Args:
            lb: Нижние границы интервалов
            ub: Верхние границы интервалов
            dir_factor: Направление (1 или -1)
            area: Требуемая площадь (энергия)
        
        Returns:
            Оптимальный уровень
        """
        n = len(lb)
        direction = 1 if dir_factor >= 0 else -1
        
        # Создание списка событий (вход/выход из интервала)
        events = []
        for i in range(n):
            events.append((lb[i] * direction, direction))
            events.append((ub[i] * direction, -direction))
        
        # Сортировка по координате, при равенстве - по убыванию фактора
        events.sort(key=lambda x: (x[0], -x[1]))
        
        level = events[0][0]
        s = 0.0
        cnt = 0
        
        for i, (coord, factor) in enumerate(events):
            if level < coord:
                break
                
            s += coord * factor
            cnt += factor
            
            if cnt > 0:
                level = (s + area) / cnt
            elif i < len(events) - 1:
                level = events[i + 1][0]
            else:
                level = coord
                
        return level * direction
    
    def get_summary(self, load_profile: List[float], 
                   eess_schedule: np.ndarray) -> dict:
        """
        Получение сводной информации о работе СНЭЭ
        
        Args:
            load_profile: Исходный профиль баланса
            eess_schedule: Рассчитанный график СНЭЭ
        
        Returns:
            Словарь с ключевыми показателями
        """
        load = np.array(load_profile)
        
        # Результирующий баланс с учетом СНЭЭ
        resulting_balance = load + eess_schedule
        
        # Энергетические показатели
        total_charge = -np.sum(eess_schedule[eess_schedule < 0])  # МВтч
        total_discharge = np.sum(eess_schedule[eess_schedule > 0])  # МВтч
        
        # Дефициты до и после
        deficit_before = -np.sum(load[load < 0])
        deficit_after = -np.sum(resulting_balance[resulting_balance < 0])
        deficit_covered = deficit_before - deficit_after
        
        # Избытки до и после
        surplus_before = np.sum(load[load > 0])
        surplus_after = np.sum(resulting_balance[resulting_balance > 0])
        surplus_utilized = surplus_before - surplus_after
        
        # Пиковые значения
        max_charge_power = -np.min(eess_schedule) if np.min(eess_schedule) < 0 else 0
        max_discharge_power = np.max(eess_schedule) if np.max(eess_schedule) > 0 else 0
        
        return {
            'total_charge_mwh': round(total_charge, 2),
            'total_discharge_mwh': round(total_discharge, 2),
            'max_charge_power_mw': round(max_charge_power, 2),
            'max_discharge_power_mw': round(max_discharge_power, 2),
            'deficit_before_mwh': round(deficit_before, 2),
            'deficit_after_mwh': round(deficit_after, 2),
            'deficit_covered_mwh': round(deficit_covered, 2),
            'deficit_coverage_percent': round(deficit_covered / deficit_before * 100, 1) if deficit_before > 0 else 0,
            'surplus_before_mwh': round(surplus_before, 2),
            'surplus_after_mwh': round(surplus_after, 2),
            'surplus_utilized_mwh': round(surplus_utilized, 2),
            'surplus_utilization_percent': round(surplus_utilized / surplus_before * 100, 1) if surplus_before > 0 else 0,
            'resulting_max_deficit_mw': round(-np.min(resulting_balance), 2),
            'resulting_max_surplus_mw': round(np.max(resulting_balance), 2),
        }


def calculate_optimal_parameters(load_profile: List[float], efficiency: float) -> Tuple[float, float]:
    """
    Расчет оптимальных параметров мощности инвертора и емкости батареи
    
    Реализация алгоритма VariatePowerAndVolume2 из VBA кода.
    Находит минимальные значения мощности и емкости, при которых
    дефицит энергии и мощности минимизируются.
    
    Args:
        load_profile: Суточный профиль баланса мощности (24 часа)
        efficiency: КПД цикла (0-1)
    
    Returns:
        Tuple (optimal_power_mw, optimal_capacity_mwh)
    """
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне (0, 1]")
    
    load = np.array(load_profile, dtype=float)
    half_cycle_eff = np.sqrt(efficiency)
    
    x_tol = 0.000001  # Погрешность по мощности
    y_tol = 0.001     # Погрешность по энергии
    im = 24
    
    # 1. Определение масштаба
    rated_power_max = np.max(np.abs(load)) * 1.1
    
    max_charge_capacity = np.sum(np.maximum(load, 0))
    max_discharge_capacity = np.sum(np.maximum(-load, 0))
    rated_capacity_max = max(max_charge_capacity, max_discharge_capacity) * 1.1
    
    # 2. Расчет минимальных дефицитов при максимальных параметрах
    calc_max = EnergyStorageCalculator(rated_power_max, rated_capacity_max, efficiency)
    eess_max = calc_max.calculate_dispatch_schedule(load_profile)
    result_max = load + eess_max
    
    min_def_max_power = -np.min(result_max)
    min_def_energy = -np.sum(result_max[result_max < 0])
    
    # 3. Определение минимальной емкости (бинарный поиск)
    lb = 0.0
    ub = rated_capacity_max
    
    while ub - lb > x_tol:
        rated_capacity_test = 0.5 * lb + 0.5 * ub
        
        calc_test = EnergyStorageCalculator(rated_power_max, rated_capacity_test, efficiency)
        eess_test = calc_test.calculate_dispatch_schedule(load_profile)
        result_test = load + eess_test
        
        def_max_power = -np.min(result_test)
        def_energy = -np.sum(result_test[result_test < 0])
        
        # Проверка критерия оптимальности
        criterion = (def_energy - min_def_energy) + im * (def_max_power - min_def_max_power)
        
        if criterion < im * y_tol:
            ub = rated_capacity_test
        else:
            lb = rated_capacity_test
    
    optimal_capacity = ub
    
    # 4. Определение минимальной мощности (бинарный поиск)
    lb = 0.0
    ub = rated_power_max
    
    while ub - lb > x_tol:
        rated_power_test = 0.5 * lb + 0.5 * ub
        
        calc_test = EnergyStorageCalculator(rated_power_test, rated_capacity_max, efficiency)
        eess_test = calc_test.calculate_dispatch_schedule(load_profile)
        result_test = load + eess_test
        
        def_max_power = -np.min(result_test)
        def_energy = -np.sum(result_test[result_test < 0])
        
        # Проверка критерия оптимальности
        criterion = (def_energy - min_def_energy) + im * (def_max_power - min_def_max_power)
        
        if criterion < im * y_tol:
            ub = rated_power_test
        else:
            lb = rated_power_test
    
    optimal_power = ub
    
    # 5. Финальная проверка
    calc_final = EnergyStorageCalculator(optimal_power, optimal_capacity, efficiency)
    eess_final = calc_final.calculate_dispatch_schedule(load_profile)
    result_final = load + eess_final
    
    def_max_power_final = -np.min(result_final)
    def_energy_final = -np.sum(result_final[result_final < 0])
    
    criterion_final = (def_energy_final - min_def_energy) + im * (def_max_power_final - min_def_max_power)
    
    # Проверка, что точка на минимуме
    assert criterion_final < 2 * im * y_tol, "Оптимальная точка не найдена"
    
    return round(optimal_power, 2), round(optimal_capacity, 2)


# =============== QP Варианты ===============

class EnergyStorageCalculator_qp:
    """Класс для расчета оптимального графика работы СНЭЭ (QP вариант)"""
    
    HOURS = 24
    
    def __init__(self, rated_power_mw: float, rated_capacity_mwh: float, efficiency: float):
        """
        Инициализация калькулятора СНЭЭ
        
        Args:
            rated_power_mw: Мощность инвертора в МВт
            rated_capacity_mwh: Емкость батареи в МВтч
            efficiency: КПД цикла (0-1)
        """
        if rated_power_mw <= 0 or rated_capacity_mwh <= 0:
            raise ValueError("Мощность и емкость должны быть положительными")
        if efficiency <= 0 or efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне (0, 1]")
            
        self.rated_power = rated_power_mw
        self.rated_capacity = rated_capacity_mwh
        self.efficiency = efficiency
        self.half_cycle_efficiency = np.sqrt(efficiency)  # КПД полуцикла
        
    def calculate_dispatch_schedule(self, load_profile: List[float]) -> np.ndarray:
        """
        Расчет диспетчерского графика СНЭЭ (QP вариант)
        
        Args:
            load_profile: Суточный профиль баланса мощности (24 часа)
                         + избыток, - дефицит
        
        Returns:
            Массив мощности СНЭЭ на шинах (24 часа)
            + разряд (выдача в сеть), - заряд (потребление из сети)
        """
        if len(load_profile) != self.HOURS:
            raise ValueError(f"Профиль должен содержать {self.HOURS} значений")
            
        load = np.array(load_profile, dtype=float)
        eess_load = np.zeros(self.HOURS)
        
        # 1. Расчет почасовых лимитов заряда и разряда
        max_charge_internal = np.minimum(
            np.maximum(load, 0),
            self.rated_power
        ) * self.half_cycle_efficiency
        
        max_discharge_internal = np.minimum(
            np.maximum(-load, 0) / self.half_cycle_efficiency,
            self.rated_power
        )
        
        sum_charge = np.sum(max_charge_internal)
        sum_discharge = np.sum(max_discharge_internal)
        
        # 2. Определение используемой энергии
        used_capacity = min(sum_charge, sum_discharge, self.rated_capacity)
        
        if used_capacity <= 0:
            return eess_load
            
        # 3. Определение уровня для заряда (water-filling)
        ub_charge = load.copy()
        lb_charge = ub_charge - (max_charge_internal / self.half_cycle_efficiency)
        charge_level = self._get_level_bounded(
            lb_charge, ub_charge, -1, used_capacity / self.half_cycle_efficiency
        )
        
        # 4. Определение уровня для разряда (water-filling)
        lb_discharge = load.copy()
        ub_discharge = lb_discharge + (max_discharge_internal * self.half_cycle_efficiency)
        discharge_level = self._get_level_bounded(
            lb_discharge, ub_discharge, 1, used_capacity * self.half_cycle_efficiency
        )
        
        # 5. Расчет почасового графика мощности
        balance = 0.0
        
        for i in range(self.HOURS):
            charge = min(
                max_charge_internal[i],
                max(load[i] - charge_level, 0) * self.half_cycle_efficiency
            )
            
            discharge = min(
                max_discharge_internal[i],
                max(discharge_level - load[i], 0) / self.half_cycle_efficiency
            )
            
            net_internal = discharge - charge
            balance += net_internal
            
            if net_internal > 0:
                # Разряд: выдаем в сеть с учетом потерь
                eess_load[i] = net_internal * self.half_cycle_efficiency
            elif net_internal < 0:
                # Заряд: забираем из сети с учетом потерь
                eess_load[i] = net_internal / self.half_cycle_efficiency
            else:
                eess_load[i] = 0.0
                
        return eess_load
    
    def _get_level_bounded(self, lb: np.ndarray, ub: np.ndarray, 
                          dir_factor: int, area: float) -> float:
        """
        Water-filling алгоритм для определения уровня заряда/разряда (QP вариант)
        
        Args:
            lb: Нижние границы интервалов
            ub: Верхние границы интервалов
            dir_factor: Направление (1 или -1)
            area: Требуемая площадь (энергия)
        
        Returns:
            Оптимальный уровень
        """
        n = len(lb)
        direction = 1 if dir_factor >= 0 else -1
        
        # Создание списка событий (вход/выход из интервала)
        events = []
        for i in range(n):
            events.append((lb[i] * direction, direction))
            events.append((ub[i] * direction, -direction))
        
        # Сортировка по координате, при равенстве - по убыванию фактора
        events.sort(key=lambda x: (x[0], -x[1]))
        
        level = events[0][0]
        s = 0.0
        cnt = 0
        
        for i, (coord, factor) in enumerate(events):
            if level < coord:
                break
                
            s += coord * factor
            cnt += factor
            
            if cnt > 0:
                level = (s + area) / cnt
            elif i < len(events) - 1:
                level = events[i + 1][0]
            else:
                level = coord
                
        return level * direction
    
    def get_summary(self, load_profile: List[float], 
                   eess_schedule: np.ndarray) -> dict:
        """
        Получение сводной информации о работе СНЭЭ (QP вариант)
        
        Args:
            load_profile: Исходный профиль баланса
            eess_schedule: Рассчитанный график СНЭЭ
        
        Returns:
            Словарь с ключевыми показателями
        """
        load = np.array(load_profile)
        
        # Результирующий баланс с учетом СНЭЭ
        resulting_balance = load + eess_schedule
        
        # Энергетические показатели
        total_charge = -np.sum(eess_schedule[eess_schedule < 0])  # МВтч
        total_discharge = np.sum(eess_schedule[eess_schedule > 0])  # МВтч
        
        # Дефициты до и после
        deficit_before = -np.sum(load[load < 0])
        deficit_after = -np.sum(resulting_balance[resulting_balance < 0])
        deficit_covered = deficit_before - deficit_after
        
        # Избытки до и после
        surplus_before = np.sum(load[load > 0])
        surplus_after = np.sum(resulting_balance[resulting_balance > 0])
        surplus_utilized = surplus_before - surplus_after
        
        # Пиковые значения
        max_charge_power = -np.min(eess_schedule) if np.min(eess_schedule) < 0 else 0
        max_discharge_power = np.max(eess_schedule) if np.max(eess_schedule) > 0 else 0
        
        return {
            'total_charge_mwh': round(total_charge, 2),
            'total_discharge_mwh': round(total_discharge, 2),
            'max_charge_power_mw': round(max_charge_power, 2),
            'max_discharge_power_mw': round(max_discharge_power, 2),
            'deficit_before_mwh': round(deficit_before, 2),
            'deficit_after_mwh': round(deficit_after, 2),
            'deficit_covered_mwh': round(deficit_covered, 2),
            'deficit_coverage_percent': round(deficit_covered / deficit_before * 100, 1) if deficit_before > 0 else 0,
            'surplus_before_mwh': round(surplus_before, 2),
            'surplus_after_mwh': round(surplus_after, 2),
            'surplus_utilized_mwh': round(surplus_utilized, 2),
            'surplus_utilization_percent': round(surplus_utilized / surplus_before * 100, 1) if surplus_before > 0 else 0,
            'resulting_max_deficit_mw': round(-np.min(resulting_balance), 2),
            'resulting_max_surplus_mw': round(np.max(resulting_balance), 2),
        }


def calculate_optimal_parameters_qp(load_profile: List[float], efficiency: float) -> Dict[str, float]:
    """
    Расчет оптимальных параметров СНЭЭ методом квадратичной оптимизации (QP)
    
    Портировано из VBA функции GetEESSOptimizedParameters.
    Решает задачу квадратичной оптимизации для нахождения оптимальных:
    - Номинальной активной входной мощности (Nin)
    - Номинальной активной выходной мощности (Nout)
    - Энергии, фактически отдаваемой в рабочем диапазоне (Capacity)
    
    Args:
        load_profile: Суточный профиль баланса мощности энергосистемы (24 часа)
                     + не покрываемое потребление, - избыток генерации
        efficiency: КПД цикла заряда-разряда (0-1)
    
    Returns:
        Dict с оптимальными параметрами:
        {
            'nin': Номинальная активная входная мощность, МВт
            'nout': Номинальная активная выходная мощность, МВт
            'capacity': Энергия, фактически отдаваемая в рабочем диапазоне, МВтч
            'deficit': Дефицит мощности результирующий, МВт
            'eens_energy_available': Массив уровней накопленной энергии (24 часа)
            'eens_load': Массив нагрузки СНЭЭ (24 часа), + разряд, - заряд
        }
    """
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне (0, 1]")
    
    im = 24  # Количество часов
    load = np.array(load_profile, dtype=float)
    
    # Размерность задачи:
    # n = im * 3 + 4 = 76 переменных
    # Переменные x:
    # x[0:23]   - dL[] - уровень накопленной энергии в батарее (Energy Available)
    # x[24:47]  - CC[] - заряд в каждый час (внутренний)
    # x[48:71]  - CD[] - разряд в каждый час (внутренний)
    # x[72]     - Dmax - дефицит мощности результирующий
    # x[73]     - Nin  - оптимальная входная мощность
    # x[74]     - Nout - оптимальная выходная мощность
    # x[75]     - C    - оптимальная емкость
    
    n = im * 3 + 4  # 76
    k = im * 5      # 120 ограничений
    
    max_real_number = 1e300
    
    # === Построение матрицы A (квадратичный член) ===
    # Почти нулевая матрица с минимальным диагональным усилением
    A = np.eye(n) * 0.00000001
    
    # === Построение вектора b (линейный член) ===
    b = np.zeros(n)
    # Веса для переменных:
    # dL[0:23], CC[24:47], CD[48:71] - вес 0
    b[72] = 1.0      # Dmax - минимизируем дефицит (наивысший приоритет)
    b[73] = 0.02     # Nin - минимизируем входную мощность
    b[74] = 0.02     # Nout - минимизируем выходную мощность
    b[75] = 0.0008   # C - минимизируем емкость
    
    # === Построение матрицы ограничений C и границ cl, cu ===
    # Линейные ограничения: cl <= C @ x <= cu
    C = np.zeros((k, n))
    cl = np.zeros(k)
    cu = np.zeros(k)
    
    # Группа 1: rL[0:23] - балансовые ограничения (изменение уровня = разряд - заряд)
    for i in range(im):
        row = i
        j = (i - 1) if i > 0 else (im - 1)  # Предыдущий час (циклически)
        
        C[row, i] = 1.0           # dL[i]
        C[row, j] = -1.0          # dL[j] (предыдущий)
        C[row, i + im] = -1.0     # -CC[i]
        C[row, i + im * 2] = 1.0  # +CD[i]
        
        cl[row] = 0.0
        cu[row] = 0.0
    
    # Группа 2: rD[0:23] - покрытие дефицита нагрузки
    for i in range(im):
        row = i + im
        
        C[row, i + im] = -1.0 / efficiency  # -CC[i] / efficiency
        C[row, i + im * 2] = 1.0            # +CD[i]
        C[row, 72] = 1.0                    # +Dmax
        
        cl[row] = load[i]
        cu[row] = max_real_number
    
    # Группа 3: rC[0:23] - ограничение емкости батареи
    for i in range(im):
        row = i + im * 2
        
        C[row, i] = -1.0     # -dL[i]
        C[row, 75] = 1.0     # +C (емкость)
        
        cl[row] = 0.0
        cu[row] = max_real_number
    
    # Группа 4: rNi[0:23] - ограничение входной мощности
    for i in range(im):
        row = i + im * 3
        
        C[row, i + im] = -1.0 / efficiency  # -CC[i] / efficiency
        C[row, 73] = 1.0                    # +Nin
        
        cl[row] = 0.0
        cu[row] = max_real_number
    
    # Группа 5: rNo[0:23] - ограничение выходной мощности
    for i in range(im):
        row = i + im * 4
        
        C[row, i + im * 2] = -1.0  # -CD[i]
        C[row, 74] = 1.0           # +Nout
        
        cl[row] = 0.0
        cu[row] = max_real_number
    
    # === Границы переменных ===
    lb = np.zeros(n)
    ub = np.full(n, max_real_number)
    
    # === Начальное приближение ===
    x0 = lb + 1.0
    
    # === Решение задачи квадратичной оптимизации ===
    # Используем метод trust-constr из scipy
    
    # Целевая функция: 0.5 * x^T @ A @ x + b^T @ x
    def objective(x):
        return 0.5 * x @ A @ x + b @ x
    
    def objective_grad(x):
        return A @ x + b
    
    def objective_hess(x):
        return A
    
    # Преобразуем cl <= C @ x <= cu в границы для scipy
    # Обрабатываем большие числа как бесконечности
    cl_processed = np.where(cl <= -1e100, -np.inf, cl)
    cu_processed = np.where(cu >= 1e100, np.inf, cu)
    
    linear_constraint = LinearConstraint(C, cl_processed, cu_processed)
    bounds = Bounds(lb, ub)
    
    # Решаем задачу оптимизации
    result = minimize(
        objective,
        x0,
        method='trust-constr',
        jac=objective_grad,
        hess=objective_hess,
        constraints=[linear_constraint],
        bounds=bounds,
        options={'maxiter': 1000, 'verbose': 0}
    )
    
    if not result.success:
        print(f"Предупреждение: оптимизация завершилась с кодом {result.status}: {result.message}")
    
    x = result.x
    
    # === Извлечение результатов ===
    dL = x[0:im]
    CC = x[im:im*2]
    CD = x[im*2:im*3]
    Dmax = x[72]
    Nin = x[73]
    Nout = x[74]
    C_capacity = x[75]
    
    # Расчет нагрузки СНЭЭ на шинах (с учетом КПД)
    eens_load = CD - CC / efficiency
    
    # Проверка баланса
    balance = np.sum(CC - CD)
    if abs(balance) > 0.001:
        print(f"Предупреждение: баланс заряд-разряд не сходится: {balance:.6f}")
    
    return {
        'nin': round(Nin, 2),
        'nout': round(Nout, 2),
        'capacity': round(C_capacity, 2),
        'deficit': round(Dmax, 2),
        'eens_energy_available': dL.tolist(),
        'eens_load': eens_load.tolist()
    }


def calculate_dispatch_schedule_qp(
    load_profile: List[float],
    nin: float,
    nout: float,
    capacity: float,
    efficiency: float
) -> Dict[str, any]:
    """
    Расчет диспетчерского графика СНЭЭ методом квадратичной оптимизации (QP)
    с заданными параметрами
    
    Портировано из VBA функции GetEESSOptimalLoad.
    Решает задачу квадратичной оптимизации для нахождения оптимального
    графика работы СНЭЭ при заданных параметрах системы.
    
    Args:
        load_profile: Суточный профиль баланса мощности энергосистемы (24 часа)
        nin: Номинальная активная входная мощность, МВт
        nout: Номинальная активная выходная мощность, МВт
        capacity: Энергия, фактически отдаваемая в рабочем диапазоне, МВтч
        efficiency: КПД цикла заряда-разряда (0-1)
    
    Returns:
        Dict с результатами расчета:
        {
            'eens_energy_available': Массив уровней накопленной энергии (24 часа)
            'eens_load': Массив нагрузки СНЭЭ (24 часа), + разряд, - заряд
            'deficit': Дефицит мощности результирующий, МВт
            'reserve': Резерв мощности результирующий, МВт
        }
    """
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне (0, 1]")
    if nin < 0 or nout < 0 or capacity < 0:
        raise ValueError("Параметры СНЭЭ должны быть неотрицательными")
    
    im = 24  # Количество часов
    load = np.array(load_profile, dtype=float)
    
    # Размерность задачи:
    # n = im * 4 + 2 = 98 переменных
    # Переменные x:
    # x[0:23]   - dL[] - уровень накопленной энергии в батарее
    # x[24:47]  - CC[] - заряд в каждый час (внутренний)
    # x[48:71]  - CD[] - разряд в каждый час (внутренний)
    # x[72:95]  - D[]  - дефицит в каждый час
    # x[96]     - Dmax - максимальный дефицит мощности
    # x[97]     - Rmax - максимальный резерв мощности
    
    n = im * 4 + 2  # 98
    k = im * 4      # 96 ограничений
    
    max_real_number = 1e300
    
    # === Построение матрицы A (квадратичный член) ===
    A = np.eye(n) * 0.00000001
    
    # === Построение вектора b (линейный член) ===
    b = np.zeros(n)
    # Веса для переменных:
    # dL[0:23], CC[24:47], CD[48:71] - вес 0
    # D[72:95] - вес 0.04 (штраф за дефицит в каждый час)
    for i in range(72, 96):
        b[i] = 0.04
    b[96] = 1.0      # Dmax - минимизируем максимальный дефицит (наивысший приоритет)
    b[97] = 0.0016   # Rmax - минимизируем максимальный резерв
    
    # === Построение матрицы ограничений C и границ cl, cu ===
    C = np.zeros((k, n))
    cl = np.zeros(k)
    cu = np.zeros(k)
    
    # Группа 1: rL[0:23] - балансовые ограничения
    for i in range(im):
        row = i
        j = (i - 1) if i > 0 else (im - 1)
        
        C[row, i] = 1.0           # dL[i]
        C[row, j] = -1.0          # dL[j]
        C[row, i + im] = -1.0     # -CC[i]
        C[row, i + im * 2] = 1.0  # +CD[i]
        
        cl[row] = 0.0
        cu[row] = 0.0
    
    # Группа 2: rD[0:23] - покрытие дефицита нагрузки
    for i in range(im):
        row = i + im
        
        C[row, i + im] = -1.0 / efficiency  # -CC[i] / efficiency
        C[row, i + im * 2] = 1.0            # +CD[i]
        C[row, i + im * 3] = 1.0            # +D[i]
        
        cl[row] = load[i]
        cu[row] = max_real_number
    
    # Группа 3: rDmin[0:23] - ограничение минимального резерва
    for i in range(im):
        row = i + im * 2
        
        C[row, i + im] = 1.0 / efficiency   # +CC[i] / efficiency
        C[row, i + im * 2] = -1.0           # -CD[i]
        C[row, 97] = 1.0                    # +Rmax
        
        cl[row] = -load[i]
        cu[row] = max_real_number
    
    # Группа 4: rDmax[0:23] - ограничение максимального дефицита
    for i in range(im):
        row = i + im * 3
        
        C[row, i + im * 3] = -1.0  # -D[i]
        C[row, 96] = 1.0           # +Dmax
        
        cl[row] = 0.0
        cu[row] = max_real_number
    
    # === Границы переменных ===
    lb = np.zeros(n)
    ub = np.full(n, max_real_number)
    
    # Ограничения на параметры СНЭЭ
    for i in range(im):
        ub[i] = capacity                    # dL[i] <= capacity
        ub[i + im] = nin * efficiency       # CC[i] <= nin * efficiency
        ub[i + im * 2] = nout               # CD[i] <= nout
    
    # === Начальное приближение ===
    x0 = lb + 1.0
    
    # === Решение задачи квадратичной оптимизации ===
    def objective(x):
        return 0.5 * x @ A @ x + b @ x
    
    def objective_grad(x):
        return A @ x + b
    
    def objective_hess(x):
        return A
    
    cl_processed = np.where(cl <= -1e100, -np.inf, cl)
    cu_processed = np.where(cu >= 1e100, np.inf, cu)
    
    linear_constraint = LinearConstraint(C, cl_processed, cu_processed)
    bounds = Bounds(lb, ub)
    
    result = minimize(
        objective,
        x0,
        method='trust-constr',
        jac=objective_grad,
        hess=objective_hess,
        constraints=[linear_constraint],
        bounds=bounds,
        options={'maxiter': 1000, 'verbose': 0}
    )
    
    if not result.success:
        print(f"Предупреждение: оптимизация завершилась с кодом {result.status}: {result.message}")
    
    x = result.x
    
    # === Извлечение результатов ===
    dL = x[0:im]
    CC = x[im:im*2]
    CD = x[im*2:im*3]
    D = x[im*3:im*4]
    Dmax = x[96]
    Rmax = x[97]
    
    # Расчет нагрузки СНЭЭ на шинах (с учетом КПД)
    eens_load = CD - CC / efficiency
    
    # Проверка баланса
    balance = np.sum(CC - CD)
    if abs(balance) > 0.001:
        print(f"Предупреждение: баланс заряд-разряд не сходится: {balance:.6f}")
    
    return {
        'eens_energy_available': dL.tolist(),
        'eens_load': eens_load.tolist(),
        'deficit': round(Dmax, 2),
        'reserve': round(Rmax, 2)
    }

