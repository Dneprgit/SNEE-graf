"""
Модуль расчета диспетчерского графика работы СНЭЭ
Портирован с VBA алгоритма water-filling
"""
import numpy as np
import io
import os
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, List, Tuple


def _to_serializable(value: Any) -> Any:
    """Преобразование numpy/scipy структур в JSON-совместимый формат."""
    if isinstance(value, np.ndarray):
        return _to_serializable(value.tolist())
    if isinstance(value, float):
        return value if np.isfinite(value) else None
    if isinstance(value, (np.floating,)):
        float_value = float(value)
        return float_value if np.isfinite(float_value) else None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_serializable(v) for v in value]
    return value


def _collect_linprog_debug(
    result: Any,
    solver_stdout: str,
    solver_stderr: str,
    c: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    bounds: List[Tuple[float, float]],
    mode: str,
) -> Dict[str, Any]:
    """Сбор подробной отладочной информации по LP задаче."""
    bounds_lb = [float(lb) for lb, _ in bounds]
    bounds_ub = [float(ub) if np.isfinite(ub) else None for _, ub in bounds]

    result_payload = {}
    if hasattr(result, "items"):
        result_payload = _to_serializable(dict(result.items()))
    else:
        result_payload = _to_serializable(result)

    return {
        "mode": mode,
        "problem_shape": {
            "variables_count": int(len(c)),
            "eq_constraints": int(A_eq.shape[0]),
            "ub_constraints": int(A_ub.shape[0]),
        },
        "objective_coefficients": _to_serializable(c),
        "constraints": {
            "A_eq_shape": [int(A_eq.shape[0]), int(A_eq.shape[1])],
            "A_ub_shape": [int(A_ub.shape[0]), int(A_ub.shape[1])],
            "b_eq": _to_serializable(b_eq),
            "b_ub": _to_serializable(b_ub),
        },
        "bounds": {
            "lower": bounds_lb,
            "upper": bounds_ub,
        },
        "solver_result": result_payload,
        "solver_stdout": solver_stdout,
        "solver_stderr": solver_stderr,
    }


def _build_colwise_sparse(matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Преобразование плотной матрицы в col-wise sparse формат для HighsLp/HighsModel."""
    starts = [0]
    indices: List[int] = []
    values: List[float] = []
    for col in range(matrix.shape[1]):
        nz_rows = np.nonzero(matrix[:, col])[0]
        for row_idx in nz_rows:
            indices.append(int(row_idx))
            values.append(float(matrix[row_idx, col]))
        starts.append(len(indices))
    return (
        np.array(starts, dtype=np.int32),
        np.array(indices, dtype=np.int32),
        np.array(values, dtype=np.float64),
    )


def _build_hessian_upper(Q: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Преобразование Hessian в upper-triangular CSC формат для highspy.passHessian."""
    n = Q.shape[0]
    starts = [0]
    indices: List[int] = []
    values: List[float] = []
    for col in range(n):
        for row in range(col + 1):
            val = Q[row, col]
            if val != 0.0:
                indices.append(row)
                values.append(float(val))
        starts.append(len(indices))
    return (
        np.array(starts, dtype=np.int32),
        np.array(indices, dtype=np.int32),
        np.array(values, dtype=np.float64),
    )


def _collect_highs_qp_debug(
    mode: str,
    c: np.ndarray,
    Q: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
    solver_status: Any,
    model_status: Any,
    model_status_str: str,
    alpha_d: float,
) -> Dict[str, Any]:
    """Сбор подробной отладочной информации для QP-решения highspy."""
    return {
        "mode": mode,
        "solver": "HiGHS.QP.highspy",
        "weights": {
            "alpha_d": alpha_d,
        },
        "problem_shape": {
            "variables_count": int(len(c)),
            "eq_constraints": int(A_eq.shape[0]),
            "ub_constraints": int(A_ub.shape[0]),
            "hessian_nonzero": int(np.count_nonzero(Q)),
        },
        "objective_coefficients": _to_serializable(c),
        "constraints": {
            "A_eq_shape": [int(A_eq.shape[0]), int(A_eq.shape[1])],
            "A_ub_shape": [int(A_ub.shape[0]), int(A_ub.shape[1])],
            "b_eq": _to_serializable(b_eq),
            "b_ub": _to_serializable(b_ub),
        },
        "bounds": {
            "lower": _to_serializable(lb),
            "upper": _to_serializable(ub),
        },
        "solver_result": {
            "run_status": str(solver_status),
            "model_status": str(model_status),
            "model_status_text": model_status_str,
        },
    }


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
    
    def __init__(self, rated_input_power_mw: float, rated_output_power_mw: float, rated_capacity_mwh: float, efficiency: float):
        """
        Инициализация калькулятора СНЭЭ
        
        Args:
            rated_input_power: Мощность входная в МВт
            rated_output_power_mw: Мощность выходная в МВт

            rated_capacity_mwh: Емкость батареи в МВтч
            efficiency: КПД цикла (0-1)
        """
        if rated_input_power_mw < 0 or rated_output_power_mw < 0 or rated_capacity_mwh < 0:
            raise ValueError("Мощность и емкость должны быть неотрицательными")
        if efficiency < 0.5 or efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне [0.5, 1]")
            
        self.rated_input_power = rated_input_power_mw
        self.rated_output_power = rated_output_power_mw
        #self.rated_power = rated_power_mw
        self.rated_capacity = rated_capacity_mwh
        self.efficiency = efficiency
        self.half_cycle_efficiency = np.sqrt(efficiency)  # КПД полуцикла


    def calculate_dispatch_schedule_qp(self, load_profile: List[float], debug: bool = False) -> dict:

        """
        Расчет диспетчерского графика СНЭЭ методом оптимизации
    
        Args:
            load_profile: Суточный профиль баланса мощности (24 часа)
            n_in: Номинальная входная мощность (МВт), >=0
            n_out: Номинальная выходная мощность (МВт), >=0
            capacity: Емкость батареи (МВтч), >=0
            efficiency: КПД цикла [0.5-1]
    
        Returns:
            Словарь с результатами:
            - eess_load: График нагрузки СНЭЭ (24 часа)
                        + разряд (выдача в сеть), - заряд (потребление из сети)
            - soc_energy: График заряда батареи (24 часа) в МВтч
            - deficit: Максимальный остаточный дефицит мощности (МВт)
            - reserve: Максимальный остаточный резерв мощности (МВт)
        """
        try:
            from scipy.optimize import linprog
        except ImportError:
            raise ImportError("Библиотека scipy не установлена. Выполните: pip install scipy")
        
        if len(load_profile) != 24:
            raise ValueError("Профиль должен содержать 24 значения")
        if self.rated_input_power < 0:
            raise ValueError("Номинальная входная мощность должна быть неотрицательной")
        if self.rated_output_power < 0:
            raise ValueError("Номинальная выходная мощность должна быть неотрицательной")
        if self.rated_capacity < 0:
            raise ValueError("Номинальная емкость должна быть неотрицательной")
        if self.efficiency < 0.5 or self.efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне [0.5, 1]")
        
        im = len(load_profile)  # количество точек
        n = im * 4 + 2  # 98 переменных: L[24] + CC[24] + CD[24] + D[24] + Dmax + Rmax
        k_eq = im  # 24 ограничения типа равенство: rL[24]
        k_ub = im * 3  # 72 ограничения типа неравенство: rD[24] + rDmax[24] + rRmax[24]
        
        # Преобразование load_profile в массив
        system_load = np.array(load_profile, dtype=float)
        
        # 1. Настройки весовых коэффициентов (из VB12)
        dmax_weight = 1.0  # максимальный дефицит мощности
        nmax_weight = dmax_weight / (im + 1)  # мощность (25 = 24 часа + 1)
        rmax_weight = nmax_weight / (im + 1)  # дефицит (25 = 24 часа + 1)
        d_weight = dmax_weight / (im + 1)  # дефицит (25 = 24 часа + 1)
        r_weight = rmax_weight / (im + 1)  # дефицит (25 = 24 часа + 1)
        
        # 2. Вектор c (веса минимизируемой функции для переменных)
        c = np.zeros(n)
        for i in range(im * 3, im * 4):  # D[0..23] - все 24 элемента
            c[i] = d_weight
        c[im * 4] = dmax_weight  # дефицит мощности
        c[im * 4 + 1] = rmax_weight  # резерв мощности
        
        # 3. Матрицы ограничений A_ub, A_eq, векторы ограничений b_ub, b_eq, cl, cu
        A_eq = np.zeros((k_eq, n))
        A_ub = np.zeros((k_ub, n))
        b_eq = np.zeros(k_eq)
        b_ub = np.zeros(k_ub)
        
        # 3.1. Ограничение rL (баланс энергии): L[i] - L[i-1] - CC[i] + CD[i] = 0
        for i in range(im):
            if i == 0:
                # Первый час: связь с последним часом
                A_eq[i, i] = 1.0          # L[0]
                A_eq[i, i + im - 1] = -1.0     # L[im-1]
                A_eq[i, i + im] = -1.0    # -CC[0]
                A_eq[i, i + im * 2] = 1.0  # CD[0]
            else:
                # Остальные часы: связь с предыдущим часом
                A_eq[i, i] = 1.0          # L[i]
                A_eq[i, i - 1] = -1.0     # L[i-1]
                A_eq[i, i + im] = -1.0    # -CC[i]
                A_eq[i, i + im * 2] = 1.0  # CD[i]
        
        # 3.2. Ограничение rD (дефицит мощности): CC[i]/η - CD[i] - D[i] <= -Load[i]
        for i in range(im):
            A_ub[i, i + im] = 1.0 / self.efficiency  # CC[i]/η
            A_ub[i, i + im * 2] = -1.0  # -CD[i]
            A_ub[i, i + im * 3] = -1.0  # -D[i]
            b_ub[i] = -system_load[i]
        
        # 3.3. Ограничение rRmax (максимальный резерв мощности):
        # Остаточный избыток S = -Load + CD - CC/η <= Rmax  => -CC/η + CD - Rmax <= Load
        for i in range(im):
            A_ub[i + im, i + im] = -1.0 / self.efficiency  # -CC[i]/η
            A_ub[i + im, i + im * 2] = 1.0  # CD[i]
            A_ub[i + im, im * 4 + 1] = -1.0  # -Rmax
            b_ub[i + im] = system_load[i]

        # 3.4. Ограничение rDmax (максимальный дефицит): D[i] - Dmax <= 0
        for i in range(im):
            A_ub[i + im * 2, i + im * 3] = 1.0  # D[i]
            A_ub[i + im * 2, im * 4] = -1.0  # -Dmax
        
        # 4. Границы переменных
        lb = np.zeros(n)
        ub = np.full(n, np.inf) # Границы для L[], CC[], CD[], Dmax, Rmax
        
        # 4.1. Границы для L[] - уровень заряда
        for i in range(im):
            ub[i] = self.rated_capacity

        # 4.2. Границы для CС[] - входная мощность заряда, если избыток
        for i in range(im):
            ub[i + im] = (min(self.rated_input_power,-system_load[i]) if system_load[i] < 0 else 0) * self.efficiency

        # 4.3. Границы для CD[] - выходная мощность разряда, если дефицит
        for i in range(im):
            ub[i + im * 2] = min(self.rated_output_power,system_load[i]) if system_load[i] > 0 else 0

        # 4.4. Границы для D[] - дефицит по часам
        # D[i] >= 0 всегда; верхняя граница не ограничиваем, чтобы не ломать выполнимость
        for i in range(im):
            ub[i + im * 3] = np.inf if system_load[i]>0 else 0

        # 4.5. Формирование ограничений для scipy (список кортежей для каждой переменной)
        bounds = [(lb[i], ub[i]) for i in range(n)]
        
        # 5. Начальное приближение не формируем

        # 6. Решение задачи оптимизации
        # На время отладки указать: options={'disp': True}
        solver_name = "SciPy.Optimize.LinProg.HiGHS. "
        linprog_stdout = io.StringIO()
        linprog_stderr = io.StringIO()
        with redirect_stdout(linprog_stdout), redirect_stderr(linprog_stderr):
            result = linprog(
                c=c,
                A_ub=A_ub,
                b_ub=b_ub,
                A_eq=A_eq,
                b_eq=b_eq,
                bounds=bounds,
                method='highs',
                options={'disp': debug}
            )
        solver_stdout = linprog_stdout.getvalue()
        solver_stderr = linprog_stderr.getvalue()
        debug_info = None
        if debug:
            debug_info = _collect_linprog_debug(
                result=result,
                solver_stdout=solver_stdout,
                solver_stderr=solver_stderr,
                c=c,
                A_eq=A_eq,
                b_eq=b_eq,
                A_ub=A_ub,
                b_ub=b_ub,
                bounds=bounds,
                mode="calculate_dispatch_schedule_qp",
            )
        
        # 7. Проверка результата: 0 - нормальное завершение, 1 - не сошелся, 2 - ограничения несовместны, 3 - задача неограничена, 4 - ошибка в алгоритме HiGHS
        if result.status > 0:
            error_messages = {
                1: "Алгоритм оптимизации не сошелся (достигнут лимит времени или итераций)",
                2: "Ограничения задачи несовместны",
                3: "Задача оптимизации неограничена",
                4: "Внутренняя ошибка алгоритма"
            }
            error_msg = solver_name + error_messages.get(result.status, f"Неизвестная ошибка оптимизации (статус: {result.status})")
            full_error = f"{error_msg}\n\nДетали: {result.message}"
            if debug and debug_info is not None:
                full_error += f"\n\nОтладка linprog:\n{debug_info}"
            print(f"Warning: {full_error}")
            raise ValueError(full_error)
        
        if result.x is None:
            no_solution_error = solver_name + "Оптимизация не вернула решение. Проверьте входные данные."
            if debug and debug_info is not None:
                no_solution_error += f"\n\nОтладка linprog:\n{debug_info}"
            raise ValueError(no_solution_error)
        
        x = result.x

        # 8. Проверка баланса заряд-разряд
        balance_check = sum(x[i + im] - x[i + im * 2] for i in range(im))
        if abs(balance_check) >= 0.001:
            warning_msg = f"Предупреждение: баланс заряд-разряд нарушен на {balance_check:.3f} МВтч"
            print(warning_msg)
            # Не выбрасываем ошибку, только предупреждаем
        
        # 9. Извлечение результатов
        # x[0..23] = L[] - уровень запаса энергии в батарее
        eens_energy_available = x[0:im]

        # x[25..48] = CC[] - мощность заряда, приведенная к выходу
        # x[49..72] = CD[] - мощность разряда
        # dblEENSLoad[i] = CD[i] - CC[i]/η, η - КПД
        eens_load = np.zeros(im)
        for i in range(im):
            eens_load[i] = x[i + im * 2] - x[i + im] / self.efficiency
        
        # x[97] = Dmax - максимальный дефицит
        system_with_enss_max_deficite = x[im * 4] # eeee
        
        # x[98] = Rmax - максимальный резерв
        system_with_enss_max_reserve = x[im * 4 + 1] # eeee
            
        result_payload = {
            'eess_load': eens_load,
            'soc_energy': eens_energy_available,
            'deficit': system_with_enss_max_deficite,
            'reserve': system_with_enss_max_reserve
        }
        if debug and debug_info is not None:
            result_payload["debug_info"] = debug_info
        return result_payload

    def calculate_dispatch_schedule_qp_highs(self, load_profile: List[float], debug: bool = False) -> dict:
        """
        Расчет диспетчерского графика СНЭЭ через реальную QP-оптимизацию HiGHS (highspy).
        """
        try:
            import highspy
        except ImportError:
            raise ImportError("Библиотека highspy не установлена. Выполните: pip install highspy")

        if len(load_profile) != 24:
            raise ValueError("Профиль должен содержать 24 значения")
        if self.rated_input_power < 0:
            raise ValueError("Номинальная входная мощность должна быть неотрицательной")
        if self.rated_output_power < 0:
            raise ValueError("Номинальная выходная мощность должна быть неотрицательной")
        if self.rated_capacity < 0:
            raise ValueError("Номинальная емкость должна быть неотрицательной")
        if self.efficiency < 0.5 or self.efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне [0.5, 1]")

        im = len(load_profile)
        n = im * 4 + 2  # L[24] + CC[24] + CD[24] + D[24] + Dmax + Rmax
        k_eq = im
        k_ub = im * 3

        system_load = np.array(load_profile, dtype=float)

        # Линейная часть цели полностью совместима с текущим LP-вариантом.
        dmax_weight = 1.0
        nmax_weight = dmax_weight / (im + 1)
        rmax_weight = nmax_weight / (im + 1)
        d_weight = dmax_weight / (im + 1)

        c = np.zeros(n)
        for i in range(im * 3, im * 4):
            c[i] = d_weight
        c[im * 4] = dmax_weight
        c[im * 4 + 1] = rmax_weight

        A_eq = np.zeros((k_eq, n))
        A_ub = np.zeros((k_ub, n))
        b_eq = np.zeros(k_eq)
        b_ub = np.zeros(k_ub)

        for i in range(im):
            if i == 0:
                A_eq[i, i] = 1.0
                A_eq[i, i + im - 1] = -1.0
                A_eq[i, i + im] = -1.0
                A_eq[i, i + im * 2] = 1.0
            else:
                A_eq[i, i] = 1.0
                A_eq[i, i - 1] = -1.0
                A_eq[i, i + im] = -1.0
                A_eq[i, i + im * 2] = 1.0

        for i in range(im):
            A_ub[i, i + im] = 1.0 / self.efficiency
            A_ub[i, i + im * 2] = -1.0
            A_ub[i, i + im * 3] = -1.0
            b_ub[i] = -system_load[i]

        for i in range(im):
            A_ub[i + im, i + im] = -1.0 / self.efficiency
            A_ub[i + im, i + im * 2] = 1.0
            A_ub[i + im, im * 4 + 1] = -1.0
            b_ub[i + im] = system_load[i]

        for i in range(im):
            A_ub[i + im * 2, i + im * 3] = 1.0
            A_ub[i + im * 2, im * 4] = -1.0

        lb = np.zeros(n)
        ub = np.full(n, np.inf)

        for i in range(im):
            ub[i] = self.rated_capacity

        for i in range(im):
            ub[i + im] = (min(self.rated_input_power, -system_load[i]) if system_load[i] < 0 else 0) * self.efficiency

        for i in range(im):
            ub[i + im * 2] = min(self.rated_output_power, system_load[i]) if system_load[i] > 0 else 0

        for i in range(im):
            ub[i + im * 3] = np.inf if system_load[i] > 0 else 0

        # Квадратичная часть цели (реальный QP): сглаживает/штрафует почасовой дефицит D[i].
        alpha_d = float(os.getenv("QP_HIGHS_ALPHA_D", "1.0"))
        Q = np.zeros((n, n))
        for i in range(im):
            idx = i + im * 3
            Q[idx, idx] = 2.0 * alpha_d

        A_all = np.vstack((A_eq, A_ub))
        row_lower = np.concatenate((b_eq, np.full(k_ub, -highspy.kHighsInf)))
        row_upper = np.concatenate((b_eq, b_ub))
        a_start, a_index, a_value = _build_colwise_sparse(A_all)
        hess_start, hess_index, hess_value = _build_hessian_upper(Q)

        model = highspy.HighsModel()
        model.lp_.num_col_ = n
        model.lp_.num_row_ = A_all.shape[0]
        model.lp_.col_cost_ = c.astype(np.float64)
        model.lp_.col_lower_ = lb.astype(np.float64)
        model.lp_.col_upper_ = ub.astype(np.float64)
        model.lp_.row_lower_ = row_lower.astype(np.float64)
        model.lp_.row_upper_ = row_upper.astype(np.float64)
        model.lp_.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        model.lp_.a_matrix_.start_ = a_start
        model.lp_.a_matrix_.index_ = a_index
        model.lp_.a_matrix_.value_ = a_value
        model.hessian_.dim_ = n
        model.hessian_.start_ = hess_start
        model.hessian_.index_ = hess_index
        model.hessian_.value_ = hess_value

        qp = highspy.Highs()
        qp.setOptionValue("output_flag", bool(debug))
        qp.passModel(model)

        run_status = qp.run()
        model_status = qp.getModelStatus()
        model_status_str = qp.modelStatusToString(model_status)

        if "Optimal" not in model_status_str:
            raise ValueError(
                "HiGHS QP не нашел оптимальное решение. "
                f"Статус: {model_status_str}"
            )

        solution = qp.getSolution()
        x = np.array(solution.col_value, dtype=float)
        if x.size != n:
            raise ValueError("HiGHS QP не вернул корректный вектор решения.")

        balance_check = sum(x[i + im] - x[i + im * 2] for i in range(im))
        if abs(balance_check) >= 0.001:
            warning_msg = f"Предупреждение: баланс заряд-разряд нарушен на {balance_check:.3f} МВтч"
            print(warning_msg)

        eens_energy_available = x[0:im]
        eens_load = np.zeros(im)
        for i in range(im):
            eens_load[i] = x[i + im * 2] - x[i + im] / self.efficiency

        system_with_enss_max_deficite = x[im * 4]
        system_with_enss_max_reserve = x[im * 4 + 1]

        result_payload = {
            "eess_load": eens_load,
            "soc_energy": eens_energy_available,
            "deficit": system_with_enss_max_deficite,
            "reserve": system_with_enss_max_reserve,
        }
        if debug:
            result_payload["debug_info"] = _collect_highs_qp_debug(
                mode="calculate_dispatch_schedule_qp_highs",
                c=c,
                Q=Q,
                A_eq=A_eq,
                b_eq=b_eq,
                A_ub=A_ub,
                b_ub=b_ub,
                lb=lb,
                ub=ub,
                solver_status=run_status,
                model_status=model_status,
                model_status_str=model_status_str,
                alpha_d=alpha_d,
            )
        return result_payload
   
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


def calculate_optimal_parameters_qp(load_profile: List[float], efficiency: float, debug: bool = False) -> dict:
    """
    Расчет оптимальных параметров через квадратичную оптимизацию (scipy)
    
    Перенос функции GetEESSOptimizedParameters из VB12 кода.
    Использует алгоритм квадратичной оптимизации с двусторонними ограничениями
    для одновременного поиска оптимальных значений входной мощности, выходной мощности и емкости.
    
    Args:
        load_profile: Суточный профиль баланса мощности (24 часа)
        efficiency: КПД цикла [0.5-1]
    
    Returns:
        dict с ключами:
        - optimal_power_in_mw: номинальная входная мощность (dblNIn)
        - optimal_power_out_mw: номинальная выходная мощность (dblNOut)
        - optimal_capacity_mwh: емкость батареи (dblCapacity)
        - deficit_mw: дефицит активной мощности (dblSystemWithENSSLoadDeficite)
    """
    try:
        from scipy.optimize import linprog
    except ImportError:
        raise ImportError("Библиотека scipy не установлена. Выполните: pip install scipy")
    
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency < 0.5 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне [0.5, 1]")
    
    im = len(load_profile)  # количество точек
    n = im * 4 + 4  # 100 переменных: L[24] + CC[24] + CD[24] + D[24] + Dmax + Nin + Nout + C
    k_eq = im  # 24 ограничения типа равенство: rL[24]
    k_ub = im * 5  # 120 ограничений типа неравенство: rD[24] + rC[24] + rNi[24] + rNo[24] + rDmax[24]
    
    # Преобразование load_profile в массив
    system_load = np.array(load_profile, dtype=float)
    
    # 1. Настройки весовых коэффициентов (из VB12)
    dmax_weight = 1.0  # максимальный дефицит мощности
    nmax_weight = dmax_weight * 0.5 / (im + 1)  # мощность (25 = 24 часа + 1)
    capacity_weight = nmax_weight / (im + 1)  # емкость (25 = 24 часа + 1)
    d_weight = nmax_weight / (im + 1)  # дефицит (25 = 24 часа + 1)
    
    # 2. Вектор c (веса минимизируемой функции для переменных)
    c = np.zeros(n)
    for i in range(im * 3, im * 4):  # D[0..23] - все 24 элемента
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
    
    # 3.1. Ограничение rL (баланс энергии): L[i] - L[i-1] - CC[i] + CD[i] = 0
    for i in range(im):
        if i == 0:
            # Первый час: связь с последним часом
            A_eq[i, i] = 1.0          # L[0]
            A_eq[i, i + im - 1] = -1.0     # L[im-1]
            A_eq[i, i + im] = -1.0    # -CC[0]
            A_eq[i, i + im * 2] = 1.0  # CD[0]
        else:
            # Остальные часы: связь с предыдущим часом
            A_eq[i, i] = 1.0          # L[i]
            A_eq[i, i - 1] = -1.0     # L[i-1]
            A_eq[i, i + im] = -1.0    # -CC[i]
            A_eq[i, i + im * 2] = 1.0  # CD[i]
    
    # 3.2. Ограничение rD (баланс мощности): CC[i]/η - CD[i] - D[i] <= -Load[i]
    for i in range(im):
        A_ub[i, i + im] = 1.0 / efficiency  # CC[i]/η
        A_ub[i, i + im * 2] = -1.0  # -CD[i]
        A_ub[i, i + im * 3] = -1.0  # -D[i]
        b_ub[i] = -system_load[i]
    
    # 3.3. Ограничение rC (емкость): L[i] - C <= 0
    for i in range(im):
        A_ub[i + im, i] = 1.0  # L[i]
        A_ub[i + im, im * 4 + 3] = -1.0  # -C
    
    # 3.4. Ограничение rNi (входная мощность): CC[i]/η - Nin <= 0
    for i in range(im):
        A_ub[i + im * 2, i + im] = 1.0 / efficiency  # CC[i]/η
        A_ub[i + im * 2, im * 4 + 1] = -1.0 if system_load[i] < 0 else 0  # -Nin
    
    # 3.5. Ограничение rNo (выходная мощность): CD[i] - Nout <= 0
    for i in range(im):
        A_ub[i + im * 3, i + im * 2] = 1.0  # CD[i]
        A_ub[i + im * 3, im * 4 + 2] = -1.0 if system_load[i] > 0 else 0 # -Nout
    
    # 3.6. Ограничение rDmax (максимальный дефицит): D[i] - Dmax <= 0
    for i in range(im):
        A_ub[i + im * 4, i + im * 3] = 1.0  # D[i]
        A_ub[i + im * 4, im * 4] = -1.0  # -Dmax
    
    # 4. Границы переменных
    lb = np.zeros(n)
    ub = np.full(n, np.inf) # Границы для L[], CC[], CD[], Dmax, Nin, Nout, C
    
    # 4.1. Границы для D[] - дефицит по часам
    # D[i] >= 0 всегда; верхняя граница не ограничиваем, чтобы не ломать выполнимость
    for i in range(im):
        ub[i + im * 3] = np.inf if system_load[i]>0 else 0

    # 4.2. Формирование ограничений для scipy (список кортежей для каждой переменной)
    bounds = [(lb[i], ub[i]) for i in range(n)]
    
    # 5. Начальное приближение не формируем

    # 6. Решение задачи оптимизации
    # На время отладки указать: options={'disp': True}
    solver_name = "SciPy.Optimize.LinProg.HiGHS. "
    linprog_stdout = io.StringIO()
    linprog_stderr = io.StringIO()
    with redirect_stdout(linprog_stdout), redirect_stderr(linprog_stderr):
        result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method='highs',
            options={'disp': debug}
        )
    solver_stdout = linprog_stdout.getvalue()
    solver_stderr = linprog_stderr.getvalue()
    debug_info = None
    if debug:
        debug_info = _collect_linprog_debug(
            result=result,
            solver_stdout=solver_stdout,
            solver_stderr=solver_stderr,
            c=c,
            A_eq=A_eq,
            b_eq=b_eq,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            mode="calculate_optimal_parameters_qp",
        )
    
    # 7. Проверка результата: 0 - нормальное завершение, 1 - не сошелся, 2 - ограничения несовместны, 3 - задача неограничена, 4 - ошибка в алгоритме HiGHS
    if result.status > 0:
        error_messages = {
            1: "Алгоритм оптимизации не сошелся (достигнут лимит времени или итераций)",
            2: "Ограничения задачи несовместны",
            3: "Задача оптимизации неограничена",
            4: "Внутренняя ошибка алгоритма"
        }
        error_msg = solver_name + error_messages.get(result.status, f"Неизвестная ошибка оптимизации (статус: {result.status})")
        full_error = f"{error_msg}\n\nДетали: {result.message}"
        if debug and debug_info is not None:
            full_error += f"\n\nОтладка linprog:\n{debug_info}"
        print(f"Warning: {full_error}")
        raise ValueError(full_error)
    
    if result.x is None:
        no_solution_error = solver_name + "Оптимизация не вернула решение. Проверьте входные данные."
        if debug and debug_info is not None:
            no_solution_error += f"\n\nОтладка linprog:\n{debug_info}"
        raise ValueError(no_solution_error)
    
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
    
    result_payload = {
        "optimal_power_in_mw": float(n_in),
        "optimal_power_out_mw": float(n_out),
        "optimal_capacity_mwh": float(capacity),
        "deficit_mw": float(system_with_enss_load_deficite)
    }
    if debug and debug_info is not None:
        result_payload["debug_info"] = debug_info
    return result_payload


