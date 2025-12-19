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
    
    # Настройки весовых коэффициентов (из VB12)
    dbl_dmax_weight = 1.0  # максимальный дефицит мощности
    dbl_d_weight = dbl_dmax_weight / 25  # дефицит мощности (25 = 24 часа + 1)
    dbl_rmax_weight = dbl_d_weight / 25  # максимальный резерв мощности
    
    # 1. Построение матрицы A (квадратичная часть целевой функции)
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
        b[i] = dbl_d_weight
    # Вес для Dmax (максимальный дефицит)
    b[im * 4] = dbl_dmax_weight
    # Вес для Rmax (резерв)
    b[im * 4 + 1] = dbl_rmax_weight
    
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
    
    # Границы для D[] - дефицит по часам (изменение из VB12)
    for i in range(im):
        lb[i + im * 3] = 0.0
        ub[i + im * 3] = max(0.0, system_load[i])  # ИЗМЕНЕНИЕ: было max_real_number
    
    # Границы для Dmax и Rmax
    lb[im * 4] = 0.0
    ub[im * 4] = max_real_number
    lb[im * 4 + 1] = 0.0
    ub[im * 4 + 1] = max_real_number
    
    # 5. Масштаб переменных (все равны 1)
    s = np.ones(n)
    
    # 6. Начальное приближение (улучшенная логика из VB12)
    x0 = np.zeros(n)
    for i in range(n):
        if ub[i] - s[i] >= lb[i] + s[i]:
            x0[i] = lb[i] + s[i]
        else:
            x0[i] = 0.5 * lb[i] + 0.5 * ub[i]
    
    # 7. Преобразование для scipy: заменяем бесконечности
    cu_finite = np.where(cu >= max_real_number / 10, np.inf, cu)
    cl_finite = np.where(cl <= -max_real_number / 10, -np.inf, cl)
    lb_finite = np.where(lb <= -max_real_number / 10, -np.inf, lb)
    ub_finite = np.where(ub >= max_real_number / 10, np.inf, ub)
    
    # 8. Определение целевой функции и её градиента
    def objective(x):
        return 0.5 * np.dot(x, np.dot(A, x)) + np.dot(b, x)
    
    def objective_grad(x):
        return np.dot(A, x) + b
    
    # 9. Формирование ограничений для scipy
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
    
    x = result.x
    
    # 12. Проверка баланса заряд-разряд
    balance_check = np.sum(x[im:im*2] - x[im*2:im*3])
    if abs(balance_check) >= 0.001:
        print(f"Warning: Charge-discharge balance check: {balance_check:.6f} МВтч (should be ~0)")
    
    return x







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
        from scipy.optimize import minimize, LinearConstraint, Bounds
    except ImportError:
        raise ImportError("Библиотека scipy не установлена. Выполните: pip install scipy")
    
    if len(load_profile) != 24:
        raise ValueError("Профиль должен содержать 24 значения")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("КПД должен быть в диапазоне (0, 1]")
    
    im = 24  # количество часов
    n = im * 4 + 4  # 100 переменных: dL[24] + CC[24] + CD[24] + D[24] + Dmax + Nin + Nout + C
    k = im * 6  # 144 ограничения: rL[24] + rD[24] + rC[24] + rNi[24] + rNo[24] + rDmax[24]
    
    max_real_number = 1e300
    
    # Преобразование load_profile в массив
    dbl_system_load = np.array(load_profile, dtype=float)
    
    # Настройки весовых коэффициентов (из VB12)
    dbl_dmax_weight = 1.0  # максимальный дефицит мощности
    dbl_nmax_weight = dbl_dmax_weight * 0.5 / 25  # мощность (25 = 24 часа + 1)
    dbl_capacity_weight = dbl_nmax_weight / 25  # емкость (25 = 24 часа + 1)
    dbl_d_weight = dbl_nmax_weight / 25  # дефицит (25 = 24 часа + 1)
    
    # 1. Построение матрицы A (квадратичная часть целевой функции)
    A = np.zeros((n, n))
    for i in range(n):
        A[i, i] = 0.00000001
    
    # 2. Вектор b (линейная часть целевой функции - веса для переменных)
    b = np.zeros(n)
    for i in range(im * 3):
        b[i] = 0.0
    for i in range(im * 3, im * 4):
        b[i] = dbl_d_weight
    b[im * 4] = dbl_dmax_weight  # дефицит мощности
    b[im * 4 + 1] = dbl_nmax_weight  # входная мощность
    b[im * 4 + 2] = dbl_nmax_weight  # выходная мощность
    b[im * 4 + 3] = dbl_capacity_weight  # емкость
    
    # 3. Матрица ограничений C и векторы cl, cu
    C = np.zeros((k, n))
    cl = np.zeros(k)
    cu = np.zeros(k)
    
    # Ограничение rL (баланс энергии): dL[i] - dL[i-1] - CC[i] + CD[i] = 0
    for i in range(im):
        j = (i - 1) if i > 0 else (im - 1)
        C[i, i] = 1.0          # dL[i]
        C[i, j] = -1.0         # dL[i-1]
        C[i, i + im] = -1.0    # -CC[i]
        C[i, i + im * 2] = 1.0  # CD[i]
        cl[i] = 0.0
        cu[i] = 0.0
    
    # Ограничение rD (баланс мощности): -CC[i]/η + CD[i] + D[i] >= Load[i]
    for i in range(im):
        C[i + im, i + im] = -1.0 / efficiency  # -CC[i]/η
        C[i + im, i + im * 2] = 1.0  # CD[i]
        C[i + im, i + im * 3] = 1.0  # D[i]
        C[i + im, im * 4] = 1.0  # Dmax
        cl[i + im] = dbl_system_load[i]
        cu[i + im] = max_real_number
    
    # Ограничение rC (емкость): -dL[i] + C >= 0
    for i in range(im):
        C[i + im * 2, i] = -1.0  # -dL[i]
        C[i + im * 2, im * 4 + 3] = 1.0  # C
        cl[i + im * 2] = 0.0
        cu[i + im * 2] = max_real_number
    
    # Ограничение rNi (входная мощность): -CC[i]/η + Nin >= 0
    for i in range(im):
        C[i + im * 3, i + im] = -1.0 / efficiency  # -CC[i]/η
        C[i + im * 3, im * 4 + 1] = 1.0  # Nin
        cl[i + im * 3] = 0.0
        cu[i + im * 3] = max_real_number
    
    # Ограничение rNo (выходная мощность): -CD[i] + Nout >= 0
    for i in range(im):
        C[i + im * 4, i + im * 2] = -1.0  # -CD[i]
        C[i + im * 4, im * 4 + 2] = 1.0  # Nout
        cl[i + im * 4] = 0.0
        cu[i + im * 4] = max_real_number
    
    # Ограничение rDmax (максимальный дефицит): -D[i] + Dmax >= 0
    for i in range(im):
        C[i + im * 5, i + im * 3] = -1.0  # -D[i]
        C[i + im * 5, im * 4] = 1.0  # Dmax
        cl[i + im * 5] = 0.0
        cu[i + im * 5] = max_real_number
    
    # 4. Границы переменных
    lb = np.zeros(n)
    ub = np.full(n, max_real_number)
    
    # Границы для dL[], CC[], CD[]
    for i in range(im):
        ub[i] = max_real_number  # L[]
        ub[i + im] = max_real_number  # CC[]
        ub[i + im * 2] = max_real_number  # CD[]
    
    # Границы для D[] - дефицит по часам
    for i in range(im):
        ub[i + im * 3] = max(0.0, dbl_system_load[i])
    
    # Границы для Dmax, Nin, Nout, C
    for i in range(im * 4, n):
        ub[i] = max_real_number
    
    # 5. Масштаб переменных (все равны 1)
    s = np.ones(n)
    
    # 6. Начальное приближение (специфичное для задачи из VB12)
    x0 = np.zeros(n)
    
    # Начальное приближение для емкости
    dbl_max_val = 0.0
    for i in range(im):
        dbl_max_val = max(lb[i] + s[i], dbl_max_val + abs(dbl_system_load[i]))
    
    # Уровень заряда [L]
    for i in range(im):
        x0[i] = dbl_max_val
    
    # Емкость
    x0[im * 4 + 3] = max(lb[im * 4 + 3], dbl_max_val) + s[im * 4 + 3]
    
    # Начальное приближение мощность заряда-разряда
    for i in range(im):
        dbl_val = max(lb[i + im] + s[i + im], lb[i + im * 2] + s[i + im * 2])
        x0[i + im] = dbl_val
        x0[i + im * 2] = dbl_val
    
    # Начальное приближение дефицит мощности
    for i in range(im):
        dbl_val = max(lb[i + im * 3], 
                     dbl_system_load[i] + x0[i + im] / efficiency - x0[i + im * 2])
        x0[i + im * 3] = dbl_val + s[i + im * 3]
    
    # Начальное приближение максимальный дефицит мощности
    dbl_max_val = lb[im * 4]
    for i in range(im):
        dbl_max_val = max(dbl_max_val, x0[i + im * 3])
    x0[im * 4] = dbl_max_val + s[im * 4]
    
    # Начальное приближение входная мощность
    dbl_max_val = lb[im * 4 + 1]
    for i in range(im):
        dbl_max_val = max(dbl_max_val, x0[i + im])
    x0[im * 4 + 1] = dbl_max_val + s[im * 4 + 1]
    
    # Начальное приближение выходная мощность
    dbl_max_val = lb[im * 4 + 2]
    for i in range(im):
        dbl_max_val = max(dbl_max_val, x0[i + im * 2])
    x0[im * 4 + 2] = dbl_max_val + s[im * 4 + 2]
    
    # 7. Преобразование для scipy: заменяем бесконечности
    cu_finite = np.where(cu >= max_real_number / 10, np.inf, cu)
    cl_finite = np.where(cl <= -max_real_number / 10, -np.inf, cl)
    lb_finite = np.where(lb <= -max_real_number / 10, -np.inf, lb)
    ub_finite = np.where(ub >= max_real_number / 10, np.inf, ub)
    
    # 8. Определение целевой функции и её градиента
    def objective(x):
        return 0.5 * np.dot(x, np.dot(A, x)) + np.dot(b, x)
    
    def objective_grad(x):
        return np.dot(A, x) + b
    
    # 9. Формирование ограничений для scipy
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
        print(f"Warning: Optimization did not converge. Status: {result.status}, Message: {result.message}")
    
    x = result.x
    
    # 12. Проверка баланса заряд-разряд
    balance_check = sum(x[i + im] - x[i + im * 2] for i in range(im))
    if abs(balance_check) >= 0.001:
        print(f"Warning: Charge-discharge balance check failed: {balance_check}")
    
    # 13. Извлечение результатов
    dbl_system_with_enss_load_deficite = x[im * 4]
    dbl_n_in = x[im * 4 + 1]
    dbl_n_out = x[im * 4 + 2]
    dbl_capacity = x[im * 4 + 3]
    
    return {
        "optimal_power_in_mw": round(dbl_n_in, 2),
        "optimal_power_out_mw": round(dbl_n_out, 2),
        "optimal_capacity_mwh": round(dbl_capacity, 2),
        "deficit_mw": round(dbl_system_with_enss_load_deficite, 2)
    } 

   def calculate_optimal_parameters_lp2(load_profile: List[float], efficiency: float) -> dict:
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
        print(f"Warning: Optimization did not converge. Status: {result.status}, Message: {result.message}")
    
    x = result.x

    # 8. Проверка баланса заряд-разряд
    balance_check = sum(x[i + im] - x[i + im * 2] for i in range(im))
    if abs(balance_check) >= 0.001:
        print(f"Warning: Charge-discharge balance check failed: {balance_check}")
    
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