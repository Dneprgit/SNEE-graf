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
    
    def _solve_qp_optimization(self, system_load: np.ndarray, dbl_n_in: float, 
                               dbl_n_out: float, dbl_capacity: float) -> np.ndarray:
        """
        Решение задачи квадратичной оптимизации методом BLEICQPSolve (аналог alglib)
        
        Минимизирует: F(x) = 0.5 * x' * A * x + b' * x
        При ограничениях: lb <= x <= ub и cl <= C' * x <= cu
        
        Args:
            system_load: Баланс мощности по часам (24 значения)
                        ВАЖНО: положительное = дефицит (потребность), отрицательное = избыток
            dbl_n_in: Номинальная входная мощность (МВт)
            dbl_n_out: Номинальная выходная мощность (МВт)
            dbl_capacity: Емкость батареи (МВтч)
        
        Returns:
            Вектор решения x (98 значений):
            x[0..23] = dL[] - энергия в батарее
            x[24..47] = CC[] - мощность заряда
            x[48..71] = CD[] - мощность разряда
            x[72..95] = D[] - дефицит мощности по часам
            x[96] = Dmax - максимальный дефицит
            x[97] = Rmax - максимальный резерв
        """
        try:
            from scipy.optimize import minimize, LinearConstraint, Bounds
        except ImportError:
            raise ImportError("Библиотека scipy не установлена. Выполните: pip install scipy")
        
        im = 24  # количество часов
        n = im * 4 + 2  # 98 переменных
        k = im * 4  # 96 ограничений
        max_real_number = 1e300
        
        # 1. Построение матрицы A (квадратичная часть целевой функции)
        # Минимальное диагональное усиление нулевой матрицы
        A = np.zeros((n, n))
        for i in range(n):
            A[i, i] = 0.00000001
        
        # 2. Вектор b (линейная часть целевой функции - веса для переменных)
        b = np.zeros(n)
        # Веса для dL, CC, CD = 0
        for i in range(im * 3):
            b[i] = 0.0
        # Веса для D[] (дефицит по часам)
        for i in range(im * 3, im * 4):
            b[i] = 0.04
        # Вес для Dmax (максимальный дефицит)
        b[im * 4] = 1.0
        # Вес для Rmax (резерв)
        b[im * 4 + 1] = 0.0016
        
        # 3. Матрица ограничений C и векторы cl, cu
        C = np.zeros((k, n))
        cl = np.zeros(k)
        cu = np.zeros(k)
        
        # Заполнение ограничений согласно VB коду
        
        # Ограничение rL (баланс энергии): dL[i] - dL[i-1] - CC[i] + CD[i] = 0
        for i in range(im):
            j = (i - 1) if i > 0 else (im - 1)  # предыдущий час (циклически)
            C[i, i] = 1.0          # dL[i]
            C[i, j] = -1.0         # dL[i-1]
            C[i, i + im] = -1.0    # -CC[i]
            C[i, i + im * 2] = 1.0  # CD[i]
            cl[i] = 0.0
            cu[i] = 0.0
        
        # Ограничение rD (баланс мощности): -CC[i]/η + CD[i] + D[i] >= SystemLoad[i]
        for i in range(im):
            C[i + im, i + im] = -1.0 / self.efficiency  # -CC[i]/η
            C[i + im, i + im * 2] = 1.0  # CD[i]
            C[i + im, i + im * 3] = 1.0  # D[i]
            cl[i + im] = system_load[i]
            cu[i + im] = max_real_number
        
        # Ограничение rDmin (ограничение резерва): CC[i]/η - CD[i] + Rmax >= -SystemLoad[i]
        for i in range(im):
            C[i + im * 2, i + im] = 1.0 / self.efficiency  # CC[i]/η
            C[i + im * 2, i + im * 2] = -1.0  # -CD[i]
            C[i + im * 2, im * 4 + 1] = 1.0  # Rmax
            cl[i + im * 2] = -system_load[i]
            cu[i + im * 2] = max_real_number
        
        # Ограничение rDmax (ограничение дефицита): -D[i] + Dmax >= 0
        for i in range(im):
            C[i + im * 3, i + im * 3] = -1.0  # -D[i]
            C[i + im * 3, im * 4] = 1.0  # Dmax
            cl[i + im * 3] = 0.0
            cu[i + im * 3] = max_real_number
        
        # 4. Границы переменных
        lb = np.zeros(n)
        ub = np.full(n, max_real_number)
        
        # Границы для dL[] - энергия в батарее
        for i in range(im):
            lb[i] = 0.0
            ub[i] = dbl_capacity
        
        # Границы для CC[] - мощность заряда
        for i in range(im):
            lb[i + im] = 0.0
            ub[i + im] = dbl_n_in * self.efficiency
        
        # Границы для CD[] - мощность разряда
        for i in range(im):
            lb[i + im * 2] = 0.0
            ub[i + im * 2] = dbl_n_out
        
        # Границы для D[] - дефицит по часам
        for i in range(im):
            lb[i + im * 3] = 0.0
            ub[i + im * 3] = max_real_number
        
        # Границы для Dmax и Rmax
        lb[im * 4] = 0.0
        ub[im * 4] = max_real_number
        lb[im * 4 + 1] = 0.0
        ub[im * 4 + 1] = max_real_number
        
        # 5. Масштаб переменных (все равны 1)
        s = np.ones(n)
        
        # 6. Начальное приближение: x0 = lb + s
        x0 = lb + s
        
        # 7. Преобразование для scipy: заменяем бесконечности
        cu_finite = np.where(cu >= max_real_number / 10, np.inf, cu)
        cl_finite = np.where(cl <= -max_real_number / 10, -np.inf, cl)
        lb_finite = np.where(lb <= -max_real_number / 10, -np.inf, lb)
        ub_finite = np.where(ub >= max_real_number / 10, np.inf, ub)
        
        # 8. Определение целевой функции и её градиента
        # F(x) = 0.5 * x' * A * x + b' * x
        def objective(x):
            return 0.5 * np.dot(x, np.dot(A, x)) + np.dot(b, x)
        
        def objective_grad(x):
            return np.dot(A, x) + b
        
        # 9. Формирование ограничений для scipy
        # LinearConstraint: cl <= C @ x <= cu
        linear_constraint = LinearConstraint(C, cl_finite, cu_finite)
        bounds = Bounds(lb_finite, ub_finite)
        
        # 10. Решение задачи оптимизации
        result = minimize(
            objective,
            x0,
            method='trust-constr',
            jac=objective_grad,
            constraints=[linear_constraint],
            bounds=bounds,
            options={'verbose': 0, 'maxiter': 2000, 'gtol': 1e-6}
        )
        
        # 11. Проверка результата
        if not result.success:
            print(f"Warning: QP Optimization did not fully converge. Status: {result.status}")
            print(f"Message: {result.message}")
            # Продолжаем с лучшим найденным решением
        
        x = result.x
        
        # 12. Проверка баланса заряд-разряд
        balance_check = np.sum(x[im:im*2] - x[im*2:im*3])
        if abs(balance_check) >= 0.001:
            print(f"Warning: Charge-discharge balance check: {balance_check:.6f} МВтч (should be ~0)")
        
        return x
        
    def calculate_dispatch_schedule_qp(self, load_profile: List[float]) -> dict:
        """
        Расчет диспетчерского графика СНЭЭ методом квадратичной оптимизации (QP)
        
        Реализация алгоритма GetEESSOptimalLoad из VB (Module1.bas).
        Использует BLEICQPSolve через scipy.optimize для поиска оптимального графика.
        
        Args:
            load_profile: Суточный профиль баланса мощности (24 часа)
                         ВАЖНО для QP: положительное = дефицит (потребность),
                                       отрицательное = избыток энергии
        
        Returns:
            Словарь с результатами:
            - eess_load: График нагрузки СНЭЭ (24 часа)
                        + разряд (выдача в сеть), - заряд (потребление из сети)
            - soc_energy: График заряда батареи (24 часа) в МВтч
            - deficit: Дефицит мощности (МВт)
            - reserve: Резерв мощности (МВт)
        """
        if len(load_profile) != self.HOURS:
            raise ValueError(f"Профиль должен содержать {self.HOURS} значений")
        
        # Преобразуем load_profile в numpy массив
        system_load = np.array(load_profile, dtype=float)
        
        # Вызов QP оптимизатора
        x = self._solve_qp_optimization(
            system_load=system_load,
            dbl_n_in=self.rated_power,
            dbl_n_out=self.rated_power,
            dbl_capacity=self.rated_capacity
        )
        
        im = 24
        
        # Извлечение результатов из вектора решения x
        # x[0..23] = dL[] - энергия в батарее
        dbl_eens_energy_available = x[0:im]
        
        # x[24..47] = CC[] - мощность заряда
        # x[48..71] = CD[] - мощность разряда
        # dblEENSLoad[i] = CD[i] - CC[i]/η (формула из VB, строка 218)
        dbl_eens_load = np.zeros(im)
        for i in range(im):
            dbl_eens_load[i] = x[i + im * 2] - x[i + im] / self.efficiency
        
        # x[96] = Dmax - максимальный дефицит
        dbl_system_with_enss_load_deficite = x[im * 4]
        
        # x[97] = Rmax - максимальный резерв
        dbl_system_with_enss_load_reserve = x[im * 4 + 1]
        
        return {
            'eess_load': dbl_eens_load,
            'soc_energy': dbl_eens_energy_available,
            'deficit': dbl_system_with_enss_load_deficite,
            'reserve': dbl_system_with_enss_load_reserve
        }
    
    def _get_level_bounded_gp(self, lb: np.ndarray, ub: np.ndarray, 
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
    
    def get_summary_qp(self, load_profile: List[float], 
                   eess_schedule: np.ndarray,
                   deficit_mw: float = None,
                   reserve_mw: float = None) -> dict:
        """
        Получение сводной информации о работе СНЭЭ (QP вариант)
        
        Args:
            load_profile: Исходный профиль баланса (для QP: + дефицит, - избыток)
            eess_schedule: Рассчитанный график СНЭЭ
            deficit_mw: Дефицит мощности из QP оптимизации (опционально)
            reserve_mw: Резерв мощности из QP оптимизации (опционально)
        
        Returns:
            Словарь с ключевыми показателями
        """
        load = np.array(load_profile)
        
        # Результирующий баланс с учетом СНЭЭ (для QP: вычитаем, так как разряд покрывает дефицит)
        resulting_balance = load - eess_schedule
        
        # Энергетические показатели
        total_charge = -np.sum(eess_schedule[eess_schedule < 0])  # МВтч
        total_discharge = np.sum(eess_schedule[eess_schedule > 0])  # МВтч
        
        # ВАЖНО: Для QP полярность баланса противоположная
        # Положительное значение = дефицит (потребность)
        # Отрицательное значение = избыток энергии
        
        # Дефициты до и после (положительные значения в load_profile)
        deficit_before = np.sum(load[load > 0])  # Изменено для QP полярности
        deficit_after = np.sum(resulting_balance[resulting_balance > 0])  # Изменено для QP полярности
        deficit_covered = deficit_before - deficit_after
        
        # Избытки до и после (отрицательные значения в load_profile)
        surplus_before = -np.sum(load[load < 0])  # Изменено для QP полярности
        surplus_after = -np.sum(resulting_balance[resulting_balance < 0])  # Изменено для QP полярности
        surplus_utilized = surplus_before - surplus_after
        
        # Пиковые значения
        max_charge_power = -np.min(eess_schedule) if np.min(eess_schedule) < 0 else 0
        max_discharge_power = np.max(eess_schedule) if np.max(eess_schedule) > 0 else 0
        
        result = {
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
            'resulting_max_deficit_mw': round(np.max(resulting_balance), 2),  # Изменено для QP полярности
            'resulting_max_surplus_mw': round(-np.min(resulting_balance), 2),  # Изменено для QP полярности
        }
        
        # Добавляем deficit и reserve из QP оптимизации, если предоставлены
        if deficit_mw is not None:
            result['deficit_mw'] = round(deficit_mw, 2)
        if reserve_mw is not None:
            result['reserve_mw'] = round(reserve_mw, 2)
        
        return result


def calculate_optimal_parameters_qp(load_profile: List[float], efficiency: float) -> dict:
    """
    Расчет оптимальных параметров через квадратичную оптимизацию (scipy)
    
    Перенос функции GetEESSOptimizedParameters из VB12 кода.
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
        from scipy.optimize import linprog, Bounds
    except ImportError:
        raise ImportError("Библиотека scipy не установлена. Выполните: pip install scipy")
    
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне (0, 1]")
    
    im = 24  # количество часов
    n = im * 4 + 4  # 100 переменных: L[24] + CC[24] + CD[24] + D[24] + Dmax + Nin + Nout + C
    k_eq = im  # 24 ограничения типа равенство: rL[24]
    k_ub = im * 5  # 120 ограничений типа неравенство: rD[24] + rC[24] + rNi[24] + rNo[24] + rDmax[24]
    
    # Преобразование load_profile в массив
    dbl_system_load = np.array(load_profile, dtype=float)
    
    # 1. Настройки весовых коэффициентов (из VB12)
    dmax_weight = 1.0  # максимальный дефицит мощности
    nmax_weight = dmax_weight * 0.5 / 25  # мощность (25 = 24 часа + 1)
    capacity_weight = nmax_weight / 25  # емкость (25 = 24 часа + 1)
    d_weight = nmax_weight / 25  # дефицит (25 = 24 часа + 1)
    
    # 2. Вектор c (веса минимизируемой функции для переменных)
    c = np.zeros(n)
    for i in range(im * 3, im * 4):
        c[i] = d_weight
    c[im * 4] = dmax_weight  # дефицит мощности
    c[im * 4 + 1] = nmax_weight  # входная мощность
    c[im * 4 + 2] = nmax_weight  # выходная мощность
    c[im * 4 + 3] = capacity_weight  # емкость
    
    # 3. Матрицы ограничений A_ub, A_eq, векторы ограничений b_ub, b_eq, cl, cu
    A_eq = np.zeros((k_eq, n))
    A_ub = np.zeros((k_ub, n))
    b_eq = np.zeros(k_eq)
    b_ub = np.zeros(k_ub)
    
    # 3.1. Ограничение rL (баланс энергии): L[i] - dL[i-1] - CC[i] + CD[i] = 0
    for i in range(im):
        j = (i - 1) if i > 0 else (im - 1)
        A_eq[i, i] = 1.0          # L[i]
        A_eq[i, j] = -1.0         # L[i-1]
        A_eq[i, i + im] = -1.0    # -CC[i]
        A_eq[i, i + im * 2] = 1.0  # CD[i]
    
    # 3.2. Ограничение rD (баланс мощности): CC[i]/η - CD[i] - D[i] <= -Load[i]
    for i in range(im):
        A_ub[i, i + im] = 1.0 / efficiency  # CC[i]/η
        A_ub[i, i + im * 2] = -1.0  # -CD[i]
        A_ub[i, i + im * 3] = -1.0  # -D[i]
        b_ub[i] = -dbl_system_load[i]
    
    # 3.3. Ограничение rC (емкость): L[i] - C <= 0
    for i in range(im):
        A_ub[i + im, i] = 1.0  # L[i]
        A_ub[i + im, im * 4 + 3] = -1.0  # -C
    
    # 3.4. Ограничение rNi (входная мощность): CC[i]/η - Nin <= 0
    for i in range(im):
        A_ub[i + im * 2, i + im] = 1.0 / efficiency  # CC[i]/η
        A_ub[i + im * 2, im * 4 + 1] = -1.0  # -Nin
    
    # 3.5. Ограничение rNo (выходная мощность): CD[i] - Nout <= 0
    for i in range(im):
        A_ub[i + im * 3, i + im * 2] = 1.0  # CD[i]
        A_ub[i + im * 3, im * 4 + 2] = -1.0  # -Nout
    
    # 3.6. Ограничение rDmax (максимальный дефицит): D[i] - Dmax <= 0
    for i in range(im):
        A_ub[i + im * 4, i + im * 3] = 1.0  # D[i]
        A_ub[i + im * 4, im * 4] = -1.0  # -Dmax
    
    # 4. Границы переменных
    lb = np.zeros(n)
    ub = np.full(n, np.inf) # Границы для dL[], CC[], CD[], Dmax, Nin, Nout, C
    
    # 4.1. Границы для D[] - дефицит по часам
    for i in range(im):
        ub[i + im * 3] = max(0.0, dbl_system_load[i])

    # 4.2. Формирование ограничений для scipy
    bounds = Bounds(lb, ub)
    
    # 5. Начальное приближение не формируем

    # 6. Решение задачи оптимизации
    # На время отладки указать: options={'disp': True}
    result = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method='highs',
        options={'disp': True}
    )
    
    # 7. Проверка результата: 0 - нормальное завершение, 1 - не сошелся, 2 - ограничения несовместны, 3 - задача неограничена, 4 - ошибка в алгоритме HiGHS
    if result.status > 0:
        error_messages = {
            1: "Алгоритм оптимизации не сошелся (достигнут лимит итераций)",
            2: "Ограничения задачи несовместны. Возможно, профиль нагрузки требует слишком большие параметры СНЭЭ",
            3: "Задача оптимизации неограничена (отсутствуют ограничения сверху)",
            4: "Внутренняя ошибка алгоритма HiGHS"
        }
        error_msg = error_messages.get(result.status, f"Неизвестная ошибка оптимизации (статус: {result.status})")
        full_error = f"{error_msg}\n\nДетали: {result.message}"
        print(f"Warning: {full_error}")
        raise ValueError(full_error)
    
    if result.x is None:
        raise ValueError("Оптимизация не вернула решение. Проверьте входные данные.")
    
    x = result.x

    # 8. Проверка баланса заряд-разряд
    balance_check = sum(x[i + im] - x[i + im * 2] for i in range(im))
    if abs(balance_check) >= 0.001:
        warning_msg = f"Предупреждение: баланс заряд-разряд нарушен на {balance_check:.3f} МВтч"
        print(warning_msg)
        # Не выбрасываем ошибку, только предупреждаем
    
    # 9. Извлечение результатов
    system_with_enss_load_deficite = x[im * 4]
    n_in = x[im * 4 + 1]
    n_out = x[im * 4 + 2]
    capacity = x[im * 4 + 3]
    
    return {
        "optimal_power_in_mw": round(n_in, 2),
        "optimal_power_out_mw": round(n_out, 2),
        "optimal_capacity_mwh": round(capacity, 2),
        "deficit_mw": round(system_with_enss_load_deficite, 2)
    } 