"""
Модуль расчета диспетчерского графика работы СНЭЭ
Портирован с VBA алгоритма water-filling
"""
import numpy as np
from typing import List, Tuple


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
    
    def __init__(self, rated_power_mw: float, rated_capacity_mwh: float, efficiency: float, 
                 rated_power_in_mw: float = None, rated_power_out_mw: float = None):
        """
        Инициализация калькулятора СНЭЭ
        
        Args:
            rated_power_mw: Мощность инвертора в МВт (используется если не указаны rated_power_in_mw и rated_power_out_mw)
            rated_capacity_mwh: Емкость батареи в МВтч
            efficiency: КПД цикла (0-1)
            rated_power_in_mw: Номинальная входная мощность в МВт (опционально)
            rated_power_out_mw: Номинальная выходная мощность в МВт (опционально)
        """
        if rated_power_mw <= 0 or rated_capacity_mwh <= 0:
            raise ValueError("Мощность и емкость должны быть положительными")
        if efficiency <= 0 or efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне (0, 1]")
            
        self.rated_power = rated_power_mw
        self.rated_capacity = rated_capacity_mwh
        self.efficiency = efficiency
        self.half_cycle_efficiency = np.sqrt(efficiency)  # КПД полуцикла
        
        # Поддержка асимметричных мощностей (Nin и Nout)
        self.rated_power_in = rated_power_in_mw if rated_power_in_mw is not None else rated_power_mw
        self.rated_power_out = rated_power_out_mw if rated_power_out_mw is not None else rated_power_mw
        
    def calculate_dispatch_schedule_qp(self, load_profile: List[float]) -> np.ndarray:
        """
        Расчет диспетчерского графика СНЭЭ через квадратичную оптимизацию (scipy)
        
        Перенос функции GetEESSOptimalLoad из VBA кода.
        Использует алгоритм квадратичной оптимизации для расчета оптимального
        графика работы СНЭЭ при известных параметрах (Nin, Nout, Capacity).
        
        Args:
            load_profile: Суточный профиль баланса мощности (24 часа)
                         + избыток, - дефицит
        
        Returns:
            Массив мощности СНЭЭ на шинах (24 часа)
            + разряд (выдача в сеть), - заряд (потребление из сети)
        """
        from scipy.optimize import minimize, LinearConstraint, Bounds
        
        if len(load_profile) != self.HOURS:
            raise ValueError(f"Профиль должен содержать {self.HOURS} значений")
        
        im = 24
        n = im * 4 + 2  # 98 переменных
        k = im * 4      # 96 ограничений
        max_real_number = 1e300
        
        load = np.array(load_profile, dtype=float)
        
        # 1. Матрица A (квадратичная часть целевой функции)
        # Диагональная матрица с малым значением для регуляризации
        A = np.eye(n) * 0.00000001
        
        # 2. Вектор b (линейная часть целевой функции)
        b = np.zeros(n)
        b[im * 3:im * 4] = 0.04      # Веса для D[i] (дефицит по часам)
        b[im * 4] = 1.0               # Вес для Dmax (максимальный дефицит)
        b[im * 4 + 1] = 0.0016        # Вес для Rmax (максимальный резерв)
        
        # 3. Матрица ограничений C и векторы cl, cu
        C = np.zeros((k, n))
        cl = np.zeros(k)
        cu = np.full(k, max_real_number)
        
        # rL: баланс энергии (24 ограничения)
        # dL[i] - dL[i-1] - CC[i] + CD[i] = 0
        for i in range(im):
            j = (i - 1) if i > 0 else (im - 1)  # Циклический индекс
            C[i, i] = 1.0           # dL[i]
            C[i, j] = -1.0          # dL[i-1]
            C[i, i + im] = -1.0     # -CC[i]
            C[i, i + im * 2] = 1.0  # CD[i]
            cl[i] = 0.0
            cu[i] = 0.0
        
        # rD: баланс мощности (24 ограничения)
        # -CC[i]/η + CD[i] + D[i] >= Load[i]
        for i in range(im):
            C[i + im, i + im] = -1.0 / self.efficiency  # -CC[i]/η
            C[i + im, i + im * 2] = 1.0                  # CD[i]
            C[i + im, i + im * 3] = 1.0                  # D[i]
            cl[i + im] = load[i]
            cu[i + im] = max_real_number
        
        # rDmin: резерв (24 ограничения)
        # CC[i]/η - CD[i] + Rmax >= -Load[i]
        for i in range(im):
            C[i + im * 2, i + im] = 1.0 / self.efficiency  # CC[i]/η
            C[i + im * 2, i + im * 2] = -1.0                # -CD[i]
            C[i + im * 2, im * 4 + 1] = 1.0                 # Rmax
            cl[i + im * 2] = -load[i]
            cu[i + im * 2] = max_real_number
        
        # rDmax: дефицит по часам (24 ограничения)
        # -D[i] + Dmax >= 0  =>  Dmax >= D[i]
        for i in range(im):
            C[i + im * 3, i + im * 3] = -1.0  # -D[i]
            C[i + im * 3, im * 4] = 1.0       # Dmax
            cl[i + im * 3] = 0.0
            cu[i + im * 3] = max_real_number
        
        # 4. Границы переменных
        lb = np.zeros(n)
        ub = np.full(n, max_real_number)
        
        # Специфичные границы
        ub[:im] = self.rated_capacity                        # dL[i]: 0 <= dL[i] <= Capacity
        ub[im:im*2] = self.rated_power_in * self.efficiency  # CC[i]: 0 <= CC[i] <= Nin * η
        ub[im*2:im*3] = self.rated_power_out                 # CD[i]: 0 <= CD[i] <= Nout
        # D[i], Dmax, Rmax: 0 <= x <= ∞ (уже установлено)
        
        # 5. Начальное приближение
        x0 = lb + 1.0
        
        # 6. Целевая функция и её градиент
        def objective(x):
            return 0.5 * np.dot(x, np.dot(A, x)) + np.dot(b, x)
        
        def objective_grad(x):
            return np.dot(A, x) + b
        
        # 7. Преобразование бесконечных значений для SciPy
        cu_finite = np.where(cu >= max_real_number / 10, np.inf, cu)
        cl_finite = np.where(cl <= -max_real_number / 10, -np.inf, cl)
        lb_finite = np.where(lb <= -max_real_number / 10, -np.inf, lb)
        ub_finite = np.where(ub >= max_real_number / 10, np.inf, ub)
        
        linear_constraint = LinearConstraint(C, cl_finite, cu_finite)
        bounds = Bounds(lb_finite, ub_finite)
        
        # 8. Решение задачи квадратичной оптимизации
        result = minimize(
            objective,
            x0,
            method='trust-constr',
            jac=objective_grad,
            constraints=[linear_constraint],
            bounds=bounds,
            options={'verbose': 0, 'maxiter': 1000}
        )
        
        if not result.success:
            print(f"Warning: QP optimization did not converge: {result.message}")
        
        x = result.x
        
        # 9. Проверка баланса (как в VB коде)
        balance = sum(x[i + im] - x[i + im * 2] for i in range(im))
        if abs(balance) >= 0.001:
            print(f"Warning: Charge-discharge balance: {balance:.6f}")
        
        # 10. Извлечение результатов
        eess_load = np.zeros(self.HOURS)
        for i in range(im):
            # График нагрузки СНЭЭ: разряд - заряд/η
            # CD[i] - CC[i]/η
            eess_load[i] = x[i + im * 2] - x[i + im] / self.efficiency
        
        # Сохраняем дополнительные результаты для возможного использования
        self._last_qp_solution = {
            'energy_available': x[:im],  # dL[i] - уровень энергии
            'charge': x[im:im*2],        # CC[i] - почасовой заряд
            'discharge': x[im*2:im*3],   # CD[i] - почасовой разряд
            'deficit_hourly': x[im*3:im*4],  # D[i] - дефицит по часам
            'deficit_max': x[im * 4],    # Dmax - максимальный дефицит
            'reserve_max': x[im * 4 + 1]  # Rmax - максимальный резерв
        }
        
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
            Словарь с ключевыми показателями, включая дополнительные параметры из QP решения
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
        
        summary = {
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
        
        # Добавление параметров из QP решения, если доступны
        if hasattr(self, '_last_qp_solution') and self._last_qp_solution:
            summary['qp_deficit_max_mw'] = round(self._last_qp_solution['deficit_max'], 2)
            summary['qp_reserve_max_mw'] = round(self._last_qp_solution['reserve_max'], 2)
        
        return summary


def calculate_optimal_parameters_qp(load_profile: List[float], efficiency: float) -> dict:
    """
    Расчет оптимальных параметров через квадратичную оптимизацию (scipy)
    
    Перенос функции GetEESSOptimizedParameters из VBA кода.
    Использует алгоритм квадратичной оптимизации с двусторонними ограничениями
    для одновременного поиска оптимальных значений входной мощности, выходной мощности и емкости.
    
    Args:
        load_profile: Суточный профиль баланса мощности (24 часа)
        efficiency: КПД цикла (0-1)
    
    Returns:
        dict с ключами:
        - optimal_power_in_mw: номинальная входная мощность (dblNIn)
        - optimal_power_out_mw: номинальная выходная мощность (dblNOut)
        - optimal_capacity_mwh: емкость батареи (dblCapacity)
        - deficit_mw: дефицит активной мощности (dblSystemWithENSSLoadDeficite)
    """
    try:
        from scipy.optimize import minimize
        from scipy.sparse import csc_matrix
    except ImportError:
        raise ImportError("Библиотека scipy не установлена. Выполните: pip install scipy")
    
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне (0, 1]")
    
    im = 24  # количество часов
    n = im * 3 + 4  # 76 переменных: dL[24] + CC[24] + CD[24] + Dmax + Nin + Nout + C
    k = im * 5  # 120 ограничений: rL[24] + rD[24] + rC[24] + rNi[24] + rNo[24]
    
    max_real_number = 1e300
    
    # Преобразование load_profile в массив (индексация с 0)
    dbl_system_load = np.array(load_profile, dtype=float)
    
    # 1. Построение матрицы A (квадратичная часть целевой функции)
    # Минимальное диагональное усиление нулевой матрицы
    A = [[0.0] * n for _ in range(n)]
    for i in range(n):
        A[i][i] = 0.00000001
    
    # 2. Вектор b (линейная часть целевой функции - веса для переменных)
    b = [0.0] * n
    for i in range(im * 3):
        b[i] = 0.0
    b[im * 3] = 1.0      # вес для Dmax (дефицит мощности)
    b[im * 3 + 1] = 0.02  # вес для Nin (входная мощность)
    b[im * 3 + 2] = 0.02  # вес для Nout (выходная мощность)
    b[im * 3 + 3] = 0.0008  # вес для C (емкость)
    
    # 3. Матрица ограничений C и векторы cl, cu
    C = [[0.0] * n for _ in range(k)]
    cl = [0.0] * k
    cu = [0.0] * k
    
    # Заполнение ограничений согласно VB коду
    # Ограничение rL (баланс энергии): dL[i] - dL[i-1] - CC[i] + CD[i] = 0
    for i in range(im):
        j = (i - 1) if i > 0 else (im - 1)  # предыдущий час (циклически)
        C[i][i] = 1.0          # dL[i]
        C[i][j] = -1.0         # dL[i-1]
        C[i][i + im] = -1.0    # -CC[i]
        C[i][i + im * 2] = 1.0  # CD[i]
        cl[i] = 0.0
        cu[i] = 0.0
    
    # Ограничение rD (баланс мощности): -CC[i]/η + CD[i] + Dmax >= Load[i]
    for i in range(im):
        C[i + im][i + im] = -1.0 / efficiency  # -CC[i]/η
        C[i + im][i + im * 2] = 1.0  # CD[i]
        C[i + im][im * 3] = 1.0  # Dmax
        cl[i + im] = dbl_system_load[i]
        cu[i + im] = max_real_number
    
    # Ограничение rC (емкость): -dL[i] + C >= 0
    for i in range(im):
        C[i + im * 2][i] = -1.0  # -dL[i]
        C[i + im * 2][im * 3 + 3] = 1.0  # C
        cl[i + im * 2] = 0.0
        cu[i + im * 2] = max_real_number
    
    # Ограничение rNi (входная мощность): -CC[i]/η + Nin >= 0
    for i in range(im):
        C[i + im * 3][i + im] = -1.0 / efficiency  # -CC[i]/η
        C[i + im * 3][im * 3 + 1] = 1.0  # Nin
        cl[i + im * 3] = 0.0
        cu[i + im * 3] = max_real_number
    
    # Ограничение rNo (выходная мощность): -CD[i] + Nout >= 0
    for i in range(im):
        C[i + im * 4][i + im * 2] = -1.0  # -CD[i]
        C[i + im * 4][im * 3 + 2] = 1.0  # Nout
        cl[i + im * 4] = 0.0
        cu[i + im * 4] = max_real_number
    
    # 4. Границы переменных (все неотрицательные)
    lb = [0.0] * n
    ub = [max_real_number] * n
    
    # 5. Масштаб переменных (все равны 1)
    s = [1.0] * n
    
    # 6. Начальное приближение: x0 = lb + s
    x0 = [lb[i] + s[i] for i in range(n)]
    
    # 7. Преобразование матриц для scipy
    A_np = np.array(A)
    b_np = np.array(b)
    C_np = np.array(C)
    cl_np = np.array(cl)
    cu_np = np.array(cu)
    lb_np = np.array(lb)
    ub_np = np.array(ub)
    x0_np = np.array(x0)
    
    # 8. Определение целевой функции и её градиента
    # F(x) = 0.5 * x' * A * x + b' * x
    def objective(x):
        return 0.5 * np.dot(x, np.dot(A_np, x)) + np.dot(b_np, x)
    
    def objective_grad(x):
        return np.dot(A_np, x) + b_np
    
    # 9. Формирование ограничений для scipy
    # LinearConstraint: cl <= C @ x <= cu
    from scipy.optimize import LinearConstraint, Bounds
    
    # Заменяем бесконечности
    cu_finite = np.where(cu_np >= max_real_number / 10, np.inf, cu_np)
    cl_finite = np.where(cl_np <= -max_real_number / 10, -np.inf, cl_np)
    lb_finite = np.where(lb_np <= -max_real_number / 10, -np.inf, lb_np)
    ub_finite = np.where(ub_np >= max_real_number / 10, np.inf, ub_np)
    
    linear_constraint = LinearConstraint(C_np, cl_finite, cu_finite)
    bounds = Bounds(lb_finite, ub_finite)
    
    # 10. Решение задачи оптимизации
    result = minimize(
        objective,
        x0_np,
        method='trust-constr',
        jac=objective_grad,
        constraints=[linear_constraint],
        bounds=bounds,
        options={'verbose': 0, 'maxiter': 1000}
    )
    
    # 11. Проверка результата
    if not result.success:
        print(f"Warning: Optimization did not converge. Status: {result.status}, Message: {result.message}")
    
    x = result.x
    
    # 12. Проверка баланса заряд-разряд
    balance_check = sum(x[i + im] - x[i + im * 2] for i in range(im))
    if abs(balance_check) >= 0.001:
        print(f"Warning: Charge-discharge balance check failed: {balance_check}")
    
    # 13. Извлечение результатов
    dbl_system_with_enss_load_deficite = x[im * 3]
    dbl_n_in = x[im * 3 + 1]
    dbl_n_out = x[im * 3 + 2]
    dbl_capacity = x[im * 3 + 3]
    
    return {
        "optimal_power_in_mw": round(dbl_n_in, 2),
        "optimal_power_out_mw": round(dbl_n_out, 2),
        "optimal_capacity_mwh": round(dbl_capacity, 2),
        "deficit_mw": round(dbl_system_with_enss_load_deficite, 2)
    }

