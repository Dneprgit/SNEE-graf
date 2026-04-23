import numpy as np
from scipy import sparse as sp

class test_qp_solver
    def __init__(self, rated_power_mw: float, rated_capacity_mwh: float, total_efficiency: float = 0.84, standby_load_mw: float = 0):
        """
        Инициализация калькулятора СНЭЭ
        
        Args:
            rated_power_mw: Мощность преобразователя в МВт
            rated_capacity_mwh: Емкость накопителя в МВтч
            total_efficiency: Энергоэффективность (0-1)
            standby_load_mw: Мощность в режиме ожидания в МВт
        """
        if rated_power_mw <= 0 or rated_capacity_mwh <= 0:
            raise ValueError("Мощность и емкость должны быть положительными")
        if total_efficiency <= 0 or total_efficiency > 1:
            raise ValueError("Энергоэффективность должна быть в диапазоне (0, 1]")
        if standby_load_mw < 0:
            raise ValueError("Мощность в режиме ожидания должна быть неотрицательная")

        self.period_length = 24 # длина расчетного периода в часах
        # характеристики цикла
        self.rated_capacity = rated_capacity_mwh
        self.total_efficiency = total_efficiency
        # почасовые данные
        self.pin_max = rated_power_mw * np.ones(self.period_length) # максимальная мощность, отбираемая из сети
        self.pout_max = rated_power_mw * np.ones(self.period_length) # максимальная мощность, отдаваемая в сеть
        self.standby_load = standby_load_mw * np.ones(self.period_length) # потребление в режиме ожидания
        self.system_load = np.zeros(self.period_length) # нагрузка системы

        efficiency = total_efficiency * (1 + 24 * standby_load_mw / rated_capacity_mwh) # эффективность по переменной части потерь при одном номинальном цикле в сутки
        if efficiency > 1:
            raise ValueError("Энергоэффективность не может превышать {(rated_capacity_mwh / (rated_capacity_mwh + 24 * standby_load_mw):.6f}")
        self.pin_eff_factor = efficiency # эффективность по переменной части потерь, относимая к мощности, отбираемой из сети

    def check(self):
        """
        Проверки данных:
        - почасовая входная мощность неотрицательная
        - почасовая выходная мощность неотрицательная
        - номинальная выходная емкость неотрицательная
        - КПД по переменным потерям должен быть в диапазоне [0.5, 1]
        - почасовое потребление в режиме ожидания неотрицательное
        """
        if min(self.pin_max) < 0:
            raise ValueError("Входная мощность должна быть неотрицательной")
        if min(self.pout_max) < 0:
            raise ValueError("Выходная мощность должна быть неотрицательной")
        if self.rated_capacity < 0:
            raise ValueError("Номинальная емкость должна быть неотрицательной")
        if self.efficiency < 0.5 or self.efficiency > 1:
            raise ValueError("КПД должен быть в диапазоне [0.5, 1]")
        if min(self.standby_load) < 0:
            raise ValueError("Потребление в режиме ожидания должно быть неотрицательным")

    def calculate_dispatch_schedule_qp_highs(self, load_profile: List[float], debug: bool = False) -> dict:
        """
        Расчет диспетчерского графика СНЭЭ квадратичной оптимизацией (HiGHS/highspy)
        """
        try:
            import highspy
        except ImportError:
            raise ImportError("Библиотека highspy не установлена. Выполните: pip install highspy")

        if len(load_profile) != self.period_length:
            raise ValueError("Профиль должен содержать {self.period_length} значений")

        self.system_load = np.array(load_profile)

        m = self.period_length
        # вспомогательные данные
        Imm = sp.identity(m)
        Zmm = sp.csc_array((m,m)) #Zmm = sp.empty((m,m))

        zm = np.zeros(m)
        inf = highspy.kHighsInf

        # размер задачи
        n = m * 2 + 2  # L[24] + EC[24] + Dmax + Rmax
        k = m * 2

        # сальдо (график без потерь)
        s = np.zeros(m)
        for i in range(m):
            s[i] = (self.pin_loss_factor if self.system_load[i] < 0.0 else 1.0) * self.system_load[i]

        # быстрая проверка возможности заряда
        if 1:
            win = sum(np.minimum(np.maximum(-s, zm), efficiency * self.pin_max)) # максимальная площадка заряда
            wsb = sum(self.standby_load) # потребление на с.н.
            if win < wsb:
                raise ValueError("Отсутствует возможность заряда для покрытия собственных нужд")

        # экстремумы графика
        smin = min(s)
        smax = max(s)
  
        # веса квадратичной части
        Q0_weight = 1E-20                    # диагональное усиление
        QCap_weight = 0.000000001            # емкость
        QEC_weight = 0.000000001             # обменная мощность
        # веса линейной части
        dmax_weight = 1.0                    # максимальный дефицит мощности
        dsum_weight = dmax_weight / (m + 1) # максимальный дефицит энергии
        rmax_weight = dsum_weight / (m + 1) # максимальный избыток мощности

        # линейная часть целевой функции
        c = np.zeros(n)
        # квадратичная часть целевой функции
        QC = Zmm
        QEC = Zmm
        QDR = sp.csc_array((2,2)) #QDR = sp.empty((2,2))

        # дообуславливание
        # максимизация уровня заряда
        QC = QC + Imm * QCap_weight
        for i in range(m):
            c[i] = c[i] - 2.0 * QCap_weight * self.rated_capacity
        # минимизация уровня обменной мощности
        QEC = QEC + Imm * QEC_weight

        # основная целевая функция
        for i in range(m): # L[]
            c[i] = c[i] + 0.0
        for i in range(m): # EC[]
            c[i + m] = c[i + m] - dsum_weight * (1.0 if s[i] > 0 else 0.0)   # максимальная выдача в часы дефицита, проверить корректность для P0 <> 0
        c[0 + 2 * m] = c[0 + 2 * m] + dmax_weight
        c[1 + 2 * m] = c[1 + 2 * m] + rmax_weight

        # Сборка матрицы Q
        Q = sp.block_diag((QC, QEC, QDR), format = "csc" )
        # диагональное усиление
        Q = Q + sp.identity(n) * Q0_weight

        # формирование ограничений
        Alb = np.zeros(k)
        Aub = np.zeros(k)
        # баланс между запасом энергии, обменной мощностью и потреблением на с.н.
        # циклическая матрица конечно-разностной схемы
        diags = np.zeros((3,m))
        diags[0,:] = -1.0
        diags[1,:] = 1.0
        diags[2,:] = -1.0
        AC = sp.spdiags(diags, [1-m,0,1], m, m)
        for i in range(m):
            Alb[i] = -self.standby_load[i]
            Aub[i] = -self.standby_load[i]
        # ограничения на максимальный дефицит и максимальный избыток
        zs = np.zeros((m, 2))
        for i in range(m):
            zs[i, 1] = 1 if s[i] > 0 else 0 # Dmax
            zs[i, 2] = -1 if s[i] <= 0 else 0 # Rmax
            Alb[i + m] = s[i] if s[i] > 0 else -inf # Dmax
            Aub[i + m] = s[i] if s[i] <= 0 else inf # Rmax
        # Сборка матрицы A
        A = sp.block_array([[AC, Imm, None], [None, Imm, zs.tocsc()], format = "csc")
        # диапазон для обменной мощности
        lb = np.zeros(n)
        ub = np.zeros(n)
        for i in range(m):
            lb[i] = 0.0 # L[]
            ub[i] = self.rated_capacity # L[]
        for i in range(m): # EC[]
            lb[i + m] = max(-efficiency * self.pin_max[i], s[i]) if s[i] <= 0 else 0
            ub[i + m] = min(self.pout_max[i], s[i]) if s[i] > 0 else 0
        # Dmax
        lb[0 + 2 * m] = 0.0 
        ub[0 + 2 * m] = smax
        # Rmax
        lb[1 + 2 * m] = 0.0 
        ub[1 + 2 * m] = -smin

        # Квадратичная часть цели (реальный QP): сглаживает/штрафует почасовой дефицит D[i].
        alpha_d = float(os.getenv("QP_HIGHS_ALPHA_D", "1.0"))

        model = highspy.HighsModel()

        model.lp_.num_col_ = n
        model.lp_.num_row_ = k

        model.lp_.col_cost_ = c.astype(np.float64)

        model.lp_.col_lower_ = lb.astype(np.float64)
        model.lp_.col_upper_ = ub.astype(np.float64)

        model.lp_.row_lower_ = Alb.astype(np.float64)
        model.lp_.row_upper_ = Aub.astype(np.float64)

        model.lp_.a_matrix_ = A # попробовать прямое назначение
"""     # если нельзя инициализовать объектов, то раскомментировать блок
        model.lp_.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        model.lp_.a_matrix_.start_ = A.indptr
        model.lp_.a_matrix_.index_ = A.indices
        model.lp_.a_matrix_.value_ = A.data
"""
        model.hessian_ = Q # попробовать прямое назначение
"""     # если нельзя инициализовать объектов, то раскомментировать блок
        model.hessian_.dim_ = n
        model.hessian_.start_ = Q.indptr
        model.hessian_.index_ = Q.indices
        model.hessian_.value_ = Q.data
"""
        qp = highspy.Highs()
        qp.setOptionValue("output_flag", bool(debug))
        qp.passModel(model)

        run_status = qp.run()
        model_status = qp.getModelStatus()
        model_status_str = qp.modelStatusToString(model_status)


        # здесь должна быть проверка model_status на kOk
        if "Optimal" not in model_status_str:
            raise ValueError(
                "HiGHS QP не нашел оптимальное решение. "
                f"Статус: {model_status_str}"
            )

        solution = qp.getSolution()
        x = np.array(solution.col_value, dtype=float)
        if x.size != n:
            raise ValueError("HiGHS QP не вернул корректный вектор решения.")

        balance_check = sum(x[i + m] + self.standby_load[i] for i in range(m))

        if abs(balance_check) >= 0.001:
            warning_msg = f"Предупреждение: баланс заряд-разряд нарушен на {balance_check:.3f} МВтч"
            print(warning_msg)

        eens_energy_available = x[0:m]
        eens_load = np.zeros(m)
        for i in range(m):
            eens_load[i] = (1 if x[i + m] > 0 else 1 / self.pin_loss_factor) * x[i + m] # учет потерь в режиме заряда

        system_with_enss_max_deficite = x[m * 2]
        system_with_enss_max_reserve = x[m * 2 + 1] / self.pin_loss_factor # учет потерь в режиме заряда

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
                A=A,
                A_lb=Alb,
                A_ub=Aub,
                lb=lb,
                ub=ub,
                solver_status=run_status,
                model_status=model_status,
                model_status_str=model_status_str,
                alpha_d=alpha_d,
            )
        return result_payload
