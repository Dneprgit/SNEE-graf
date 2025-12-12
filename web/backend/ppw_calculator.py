"""
PPW Calculator - портирование алгоритмов из VB для второго варианта СНЭЭ
Использует квадратичную оптимизацию для расчета оптимальных параметров и графиков нагрузки
"""
import numpy as np
from typing import Tuple, List
from quadratic_optimizer import solve_qp_problem, check_termination_code


MAX_REAL_NUMBER = np.inf  # Используем np.inf вместо больших чисел


class PPWCalculator:
    """Калькулятор для второго варианта СНЭЭ с квадратичной оптимизацией"""
    
    HOURS = 24
    
    def __init__(self, efficiency: float):
        """
        Инициализация калькулятора
        
        Args:
            efficiency: КПД цикла (0-1)
        """
        if efficiency <= 0 or efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне (0, 1]")
        self.efficiency = efficiency
    
    def calculate_optimal_load(self, 
                               system_load: List[float],
                               rated_power_in: float,
                               rated_power_out: float,
                               capacity: float) -> Tuple[np.ndarray, np.ndarray, float, float, int]:
        """
        Расчет оптимального графика нагрузки СНЭЭ при заданных параметрах
        Портирование функции GetEESSOptimalLoad из VB
        
        Args:
            system_load: Суточный баланс мощности энергосистемы (24 значения)
            rated_power_in: Номинальная активная входная мощность (МВт)
            rated_power_out: Номинальная активная выходная мощность (МВт)
            capacity: Энергия, фактически отдаваемая в рабочем диапазоне (МВтч)
        
        Returns:
            Tuple[np.ndarray, np.ndarray, float, float, int]:
                - eess_energy_available: Энергия в батарее на каждый час (24 значения)
                - eess_load: График нагрузки СНЭЭ (24 значения, + разряд, - заряд)
                - system_load_deficit: Дефицит мощности с учетом СНЭЭ
                - system_load_reserve: Резерв мощности с учетом СНЭЭ
                - termination_code: Код завершения оптимизации
        """
        if len(system_load) != self.HOURS:
            raise ValueError(f"system_load должен содержать {self.HOURS} значений")
        
        im = self.HOURS
        n = im * 4 + 2  # Размерность задачи: 98
        k = im * 4      # Количество ограничений: 96
        
        # Инициализация массивов
        A = np.eye(n) * 1e-8  # Минимальное диагональное усиление нулевой матрицы
        b = np.zeros(n)
        C = np.zeros((k, n))
        cl = np.zeros(k)
        cu = np.zeros(k)
        lb = np.zeros(n)
        ub = np.zeros(n)
        s = np.ones(n)  # Масштаб = 1
        x0 = lb + s     # Начальное приближение
        
        # Веса для целевой функции
        for i in range(im * 3):
            b[i] = 0
        for i in range(im * 3, im * 4):
            b[i] = 0.04
        b[im * 4] = 1       # Dmax
        b[im * 4 + 1] = 0.0016  # Rmax
        
        # Ограничения
        # Переменные: dL[0..23], CC[24..47], CD[48..71], D[72..95], Dmax[96], Rmax[97]
        
        # rL: связь dL между часами с учетом заряда/разряда
        for i in range(im):
            j = (i - 1) if i > 0 else (im - 1)
            C[i, i] = 1         # dL[i]
            C[i, j] = -1        # dL[j]
            C[i, i + im] = -1   # CC[i]
            C[i, i + im * 2] = 1  # CD[i]
            cl[i] = 0
            cu[i] = 0
        
        # rD: баланс мощности с учетом разряда
        for i in range(im):
            C[i + im, i + im] = -1 / self.efficiency  # CC[i]
            C[i + im, i + im * 2] = 1                 # CD[i]
            C[i + im, i + im * 3] = 1                 # D[i]
            cl[i + im] = system_load[i]
            cu[i + im] = MAX_REAL_NUMBER
        
        # rDmin: ограничение на минимальный дефицит с резервом
        for i in range(im):
            C[i + im * 2, i + im] = 1 / self.efficiency  # CC[i]
            C[i + im * 2, i + im * 2] = -1               # CD[i]
            C[i + im * 2, n - 1] = 1                     # Rmax
            cl[i + im * 2] = -system_load[i]
            cu[i + im * 2] = MAX_REAL_NUMBER
        
        # rDmax: ограничение на максимальный дефицит
        for i in range(im):
            C[i + im * 3, i + im * 3] = -1  # D[i]
            C[i + im * 3, n - 2] = 1        # Dmax
            cl[i + im * 3] = 0
            cu[i + im * 3] = MAX_REAL_NUMBER
        
        # Границы переменных
        for i in range(n):
            lb[i] = 0
        
        # dL: энергия в батарее
        for i in range(im):
            ub[i] = capacity
        
        # CC: заряд с учетом КПД
        for i in range(im):
            ub[i + im] = rated_power_in * self.efficiency
        
        # CD: разряд
        for i in range(im):
            ub[i + im * 2] = rated_power_out
        
        # D: дефицит
        for i in range(im):
            ub[i + im * 3] = MAX_REAL_NUMBER
        
        # Dmax, Rmax
        ub[n - 2] = MAX_REAL_NUMBER  # Dmax
        ub[n - 1] = MAX_REAL_NUMBER  # Rmax
        
        # Решение задачи оптимизации
        x, termination_code = solve_qp_problem(n, k, A, b, C, cl, cu, lb, ub, s, x0)
        
        # Проверка кода завершения
        success, message = check_termination_code(termination_code)
        if not success and termination_code not in [1, 5, 7, 8]:
            print(f"Warning: Optimization exit code = {termination_code}: {message}")
        
        # Проверка баланса
        charge_total = np.sum(x[im:im * 2])
        discharge_total = np.sum(x[im * 2:im * 3])
        balance = abs(charge_total - discharge_total)
        if balance > 0.001:
            print(f"Warning: Charge-discharge balance = {balance:.6f} (should be near 0)")
        
        # Извлечение результатов
        eess_energy_available = x[:im]  # dL
        cc = x[im:im * 2]                # CC (заряд внутри батареи)
        cd = x[im * 2:im * 3]           # CD (разряд внутри батареи)
        
        # График нагрузки СНЭЭ на шинах
        eess_load = np.zeros(im)
        for i in range(im):
            # Разряд: выдаем в сеть с учетом потерь
            # Заряд: забираем из сети с учетом потерь
            eess_load[i] = cd[i] - cc[i] / self.efficiency
        
        system_load_deficit = x[n - 2]  # Dmax
        system_load_reserve = x[n - 1]  # Rmax
        
        return eess_energy_available, eess_load, system_load_deficit, system_load_reserve, termination_code
    
    def calculate_optimized_parameters(self, 
                                      system_load: List[float]) -> Tuple[float, float, float, np.ndarray, np.ndarray, float, int]:
        """
        Расчет оптимальных параметров СНЭЭ
        Портирование функции GetEESSOptimizedParameters из VB
        
        Args:
            system_load: Суточный баланс мощности энергосистемы (24 значения)
        
        Returns:
            Tuple[float, float, float, np.ndarray, np.ndarray, float, int]:
                - rated_power_in: Оптимальная номинальная активная входная мощность (МВт)
                - rated_power_out: Оптимальная номинальная активная выходная мощность (МВт)
                - capacity: Оптимальная энергия в рабочем диапазоне (МВтч)
                - eess_energy_available: Энергия в батарее на каждый час (24 значения)
                - eess_load: График нагрузки СНЭЭ (24 значения)
                - system_load_deficit: Дефицит мощности с учетом СНЭЭ
                - termination_code: Код завершения оптимизации
        """
        if len(system_load) != self.HOURS:
            raise ValueError(f"system_load должен содержать {self.HOURS} значений")
        
        im = self.HOURS
        n = im * 3 + 4  # Размерность задачи: 76
        k = im * 5      # Количество ограничений: 120
        
        # Инициализация массивов
        A = np.eye(n) * 1e-8  # Минимальное диагональное усиление
        b = np.zeros(n)
        C = np.zeros((k, n))
        cl = np.zeros(k)
        cu = np.zeros(k)
        lb = np.zeros(n)
        ub = np.zeros(n)
        s = np.ones(n)
        x0 = lb + s
        
        # Веса для целевой функции
        for i in range(im * 3):
            b[i] = 0
        b[im * 3] = 1        # Dmax
        b[im * 3 + 1] = 0.02  # Nin
        b[im * 3 + 2] = 0.02  # Nout
        b[im * 3 + 3] = 0.0008  # C
        
        # Ограничения
        # Переменные: dL[0..23], CC[24..47], CD[48..71], Dmax[72], Nin[73], Nout[74], C[75]
        
        # rL: связь dL между часами
        for i in range(im):
            j = (i - 1) if i > 0 else (im - 1)
            C[i, i] = 1         # dL[i]
            C[i, j] = -1        # dL[j]
            C[i, i + im] = -1   # CC[i]
            C[i, i + im * 2] = 1  # CD[i]
            cl[i] = 0
            cu[i] = 0
        
        # rD: баланс мощности
        for i in range(im):
            C[i + im, i + im] = -1 / self.efficiency  # CC[i]
            C[i + im, i + im * 2] = 1                 # CD[i]
            C[i + im, im * 3] = 1                     # Dmax
            cl[i + im] = system_load[i]
            cu[i + im] = MAX_REAL_NUMBER
        
        # rC: ограничение емкости
        for i in range(im):
            C[i + im * 2, i] = -1       # dL[i]
            C[i + im * 2, n - 1] = 1    # C
            cl[i + im * 2] = 0
            cu[i + im * 2] = MAX_REAL_NUMBER
        
        # rNi: ограничение входной мощности
        for i in range(im):
            C[i + im * 3, i + im] = -1 / self.efficiency  # CC[i]
            C[i + im * 3, n - 3] = 1                      # Nin
            cl[i + im * 3] = 0
            cu[i + im * 3] = MAX_REAL_NUMBER
        
        # rNo: ограничение выходной мощности
        for i in range(im):
            C[i + im * 4, i + im * 2] = -1  # CD[i]
            C[i + im * 4, n - 2] = 1        # Nout
            cl[i + im * 4] = 0
            cu[i + im * 4] = MAX_REAL_NUMBER
        
        # Границы переменных
        for i in range(n):
            lb[i] = 0
            ub[i] = MAX_REAL_NUMBER
        
        # Решение задачи оптимизации
        x, termination_code = solve_qp_problem(n, k, A, b, C, cl, cu, lb, ub, s, x0)
        
        # Проверка кода завершения
        success, message = check_termination_code(termination_code)
        if not success and termination_code not in [1, 5, 7, 8]:
            print(f"Warning: Optimization exit code = {termination_code}: {message}")
        
        # Проверка баланса
        charge_total = np.sum(x[im:im * 2])
        discharge_total = np.sum(x[im * 2:im * 3])
        balance = abs(charge_total - discharge_total)
        if balance > 0.001:
            print(f"Warning: Charge-discharge balance = {balance:.6f}")
        
        # Извлечение результатов
        eess_energy_available = x[:im]
        cc = x[im:im * 2]
        cd = x[im * 2:im * 3]
        
        system_load_deficit = x[im * 3]
        rated_power_in = x[im * 3 + 1]
        rated_power_out = x[im * 3 + 2]
        capacity = x[im * 3 + 3]
        
        # График нагрузки СНЭЭ
        eess_load = np.zeros(im)
        for i in range(im):
            eess_load[i] = cd[i] - cc[i] / self.efficiency
        
        return rated_power_in, rated_power_out, capacity, eess_energy_available, eess_load, system_load_deficit, termination_code
    
    def get_summary(self, system_load: List[float], eess_load: np.ndarray) -> dict:
        """
        Получение сводной информации о работе СНЭЭ
        
        Args:
            system_load: Исходный профиль баланса
            eess_load: Рассчитанный график СНЭЭ
        
        Returns:
            Словарь с ключевыми показателями
        """
        load = np.array(system_load)
        
        # Результирующий баланс с учетом СНЭЭ
        resulting_balance = load + eess_load
        
        # Энергетические показатели
        total_charge = -np.sum(eess_load[eess_load < 0])  # МВтч
        total_discharge = np.sum(eess_load[eess_load > 0])  # МВтч
        
        # Дефициты до и после
        deficit_before = -np.sum(load[load < 0])
        deficit_after = -np.sum(resulting_balance[resulting_balance < 0])
        deficit_covered = deficit_before - deficit_after
        
        # Избытки до и после
        surplus_before = np.sum(load[load > 0])
        surplus_after = np.sum(resulting_balance[resulting_balance > 0])
        surplus_utilized = surplus_before - surplus_after
        
        # Пиковые значения
        max_charge_power = -np.min(eess_load) if np.min(eess_load) < 0 else 0
        max_discharge_power = np.max(eess_load) if np.max(eess_load) > 0 else 0
        
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

