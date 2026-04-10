import os
from typing import Any, Dict, List

import numpy as np
from scipy import sparse as sp


def _to_serializable(value: Any) -> Any:
    """Преобразование numpy/scipy структур в JSON-совместимый формат."""
    if isinstance(value, np.ndarray):
        return _to_serializable(value.tolist())
    if isinstance(value, (np.floating, float)):
        float_value = float(value)
        return float_value if np.isfinite(float_value) else None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_serializable(v) for v in value]
    return value


def _collect_highs_qp_debug_modified(
    *,
    mode: str,
    c: np.ndarray,
    Q: np.ndarray,
    A: np.ndarray,
    row_lower: np.ndarray,
    row_upper: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
    solver_status: Any,
    model_status: Any,
    model_status_str: str,
    alpha_d: float,
    standby_load_mw: float,
    model: Any,
) -> Dict[str, Any]:
    """Сбор подробной отладочной информации для модифицированного HiGHS QP."""
    return {
        "mode": mode,
        "solver": "HiGHS.QP.highspy.modified",
        "weights": {
            "alpha_d": alpha_d,
        },
        "standby_load_mw": standby_load_mw,
        "problem_shape": {
            "variables_count": int(len(c)),
            "constraints_count": int(A.shape[0]),
            "hessian_nonzero": int(np.count_nonzero(Q)),
        },
        "objective_coefficients": _to_serializable(c),
        "constraints": {
            "A_shape": [int(A.shape[0]), int(A.shape[1])],
            "row_lower": _to_serializable(row_lower),
            "row_upper": _to_serializable(row_upper),
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
        "highs_model": {
            "lp": {
                "a_matrix": {
                    "format": str(model.lp_.a_matrix_.format_),
                    "start": _to_serializable(model.lp_.a_matrix_.start_),
                    "index": _to_serializable(model.lp_.a_matrix_.index_),
                    "value": _to_serializable(model.lp_.a_matrix_.value_),
                },
            },
            "hessian": {
                "dim": int(model.hessian_.dim_),
                "start": _to_serializable(model.hessian_.start_),
                "index": _to_serializable(model.hessian_.index_),
                "value": _to_serializable(model.hessian_.value_),
            },
        }
    }


class TestQpSolverModified:
    """
    Модифицированный QP-решатель диспетчерского графика СНЭЭ.

    Особенность модификации: учитывается постоянная нагрузка собственных нужд
    `standby_load_mw`, а также ее влияние на эквивалентный КПД по переменной
    части потерь (`pin_loss_factor`).
    """

    def __init__(
        self,
        rated_power_mw: float,
        rated_capacity_mwh: float,
        total_efficiency: float = 0.84,
        standby_load_mw: float = 0.0,
    ) -> None:
        """
        Инициализация калькулятора СНЭЭ.

        Args:
            rated_power_mw: Мощность преобразователя в МВт (используется симметрично).
            rated_capacity_mwh: Емкость накопителя в МВтч.
            total_efficiency: Полный КПД цикла (0..1).
            standby_load_mw: Почасовое потребление в режиме ожидания, МВт.
        """
        if rated_power_mw <= 0 or rated_capacity_mwh <= 0:
            raise ValueError("Мощность и емкость должны быть положительными")
        if total_efficiency <= 0 or total_efficiency > 1:
            raise ValueError("Энергоэффективность должна быть в диапазоне (0, 1]")
        if standby_load_mw < 0:
            raise ValueError("Мощность в режиме ожидания должна быть неотрицательной")

        self.period_length = 24  # длина расчетного периода в часах
        self.rated_capacity = float(rated_capacity_mwh)
        self.total_efficiency = float(total_efficiency)
        self.pin_max = float(rated_power_mw) * np.ones(self.period_length)
        self.pout_max = float(rated_power_mw) * np.ones(self.period_length)
        self.standby_load = float(standby_load_mw) * np.ones(self.period_length)
        self.system_load = np.zeros(self.period_length)

        # КПД переменной части потерь (учет суточного расхода на standby)
        eff_var = total_efficiency * (1 + 24 * standby_load_mw / rated_capacity_mwh)
        max_total_eff = rated_capacity_mwh / (rated_capacity_mwh + 24 * standby_load_mw)
        if eff_var > 1:
            raise ValueError(
                f"Энергоэффективность не может превышать {max_total_eff:.6f} "
                "при текущем standby_load_mw"
            )
        if eff_var < 0.5:
            raise ValueError("КПД по переменным потерям должен быть в диапазоне [0.5, 1]")
        self.pin_loss_factor = float(eff_var)
        self.standby_load_mw = float(standby_load_mw)

    def check(self) -> None:
        """Базовые проверки ограничений и параметров модели."""
        if np.min(self.pin_max) < 0:
            raise ValueError("Входная мощность должна быть неотрицательной")
        if np.min(self.pout_max) < 0:
            raise ValueError("Выходная мощность должна быть неотрицательной")
        if self.rated_capacity < 0:
            raise ValueError("Номинальная емкость должна быть неотрицательной")
        if self.pin_loss_factor < 0.5 or self.pin_loss_factor > 1:
            raise ValueError("КПД должен быть в диапазоне [0.5, 1]")
        if np.min(self.standby_load) < 0:
            raise ValueError("Потребление в режиме ожидания должно быть неотрицательным")

    def calculate_dispatch_schedule_qp_highs_modified(
        self,
        load_profile: List[float],
        debug: bool = False,
    ) -> dict:
        """
        Расчет диспетчерского графика СНЭЭ квадратичной оптимизацией (HiGHS/highspy).

        Возвращает:
            - eess_load: график мощности СНЭЭ (+ разряд, - заряд)
            - soc_energy: запас энергии в батарее по часам
            - deficit: максимальный дефицит мощности (Dmax)
            - reserve: максимальный избыток мощности (Rmax) с учетом потерь
            - debug_info: расширенная отладочная информация (если debug=True)
        """
        try:
            import highspy
        except ImportError as exc:
            raise ImportError(
                "Библиотека highspy не установлена. Выполните: pip install highspy"
            ) from exc

        if len(load_profile) != self.period_length:
            raise ValueError(f"Профиль должен содержать {self.period_length} значений")

        self.check()
        self.system_load = np.array(load_profile, dtype=float)

        m = self.period_length
        # вспомогательные данные
        imm = sp.identity(m, format="csc")
        zmm = sp.csc_array((m, m))
        z2 = sp.csc_array((2, 2))

        inf = highspy.kHighsInf
        # размер задачи
        n = m * 2 + 2  # L[24] + EC[24] + Dmax + Rmax
        k = m * 2

        # сальдо (график без потерь)
        s = np.zeros(m)
        for i in range(m):
            s[i] = (
                self.pin_loss_factor if self.system_load[i] < 0.0 else 1.0
            ) * self.system_load[i]

        # быстрая проверка возможности заряда для покрытия standby-потребления
        max_charge_window = np.sum(
            np.minimum(np.maximum(-s, np.zeros(m)), self.pin_loss_factor * self.pin_max)
        )
        standby_need = float(np.sum(self.standby_load))
        if max_charge_window < standby_need:
            raise ValueError("Отсутствует возможность заряда для покрытия собственных нужд")

        smin = float(np.min(s))
        smax = float(np.max(s))

        # веса квадратичной части
        q0_weight = 1e-20  # диагональное усиление
        qcap_weight = 1e-9  # емкость
        qec_weight = 1e-9  # обменная мощность
        # веса линейной части
        dmax_weight = 1.0
        dsum_weight = dmax_weight / (m + 1)
        rmax_weight = dsum_weight / (m + 1)

        # линейная часть целевой функции
        c = np.zeros(n)
        # квадратичная часть целевой функции
        qc = zmm + imm * qcap_weight
        qec = zmm + imm * qec_weight
        qdr = z2

        # дообуславливание: максимизация уровня заряда и минимизация обменной мощности
        for i in range(m):
            c[i] -= 2.0 * qcap_weight * self.rated_capacity
            # основная целевая функция для EC[]:
            # максимальная выдача в часы дефицита
            c[i + m] -= dsum_weight * (1.0 if s[i] > 0 else 0.0)
        c[2 * m] += dmax_weight
        c[2 * m + 1] += rmax_weight

        # сборка матрицы Q
        q = sp.block_diag((qc, qec, qdr), format="csc")
        # диагональное усиление
        q = q + sp.identity(n, format="csc") * q0_weight

        # формирование ограничений
        alb = np.zeros(k)
        aub = np.zeros(k)

        # баланс между запасом энергии, обменной мощностью и потреблением на с.н.
        # циклическая матрица конечно-разностной схемы
        diags = np.zeros((3, m))
        diags[0, :] = -1.0
        diags[1, :] = 1.0
        diags[2, :] = -1.0
        ac = sp.spdiags(diags, [1 - m, 0, 1], m, m).tocsc()

        for i in range(m):
            alb[i] = -self.standby_load[i]
            aub[i] = -self.standby_load[i]

        # ограничения на максимальный дефицит и максимальный избыток
        zs = np.zeros((m, 2))
        for i in range(m):
            zs[i, 0] = 1.0 if s[i] > 0 else 0.0
            zs[i, 1] = -1.0 if s[i] <= 0 else 0.0
            alb[i + m] = s[i] if s[i] > 0 else -inf
            aub[i + m] = s[i] if s[i] <= 0 else inf

        # сборка матрицы A
        a = sp.block_array(
            [[ac, imm, None], [None, imm, sp.csc_array(zs)]],
            format="csc",
        )

        # диапазон для переменных
        lb = np.zeros(n)
        ub = np.zeros(n)
        for i in range(m):
            lb[i] = 0.0
            ub[i] = self.rated_capacity
        for i in range(m):
            lb[i + m] = (
                max(-self.pin_loss_factor * self.pin_max[i], s[i]) if s[i] <= 0 else 0.0
            )
            ub[i + m] = min(self.pout_max[i], s[i]) if s[i] > 0 else 0.0
        lb[2 * m] = 0.0
        ub[2 * m] = smax
        lb[2 * m + 1] = 0.0
        ub[2 * m + 1] = -smin

        # # квадратичная часть цели (реальный QP): штрафует почасовой обмен EC[i]
        alpha_d = float(os.getenv("QP_HIGHS_ALPHA_D", "1.0"))
        for i in range(m):
            idx = i + m
            q[idx, idx] = q[idx, idx] + 2.0 * alpha_d

        # наполнение модели HiGHS в col-wise sparse формате
        model = highspy.HighsModel()
        model.lp_.num_col_ = n
        model.lp_.num_row_ = k
        model.lp_.col_cost_ = c.astype(np.float64)
        model.lp_.col_lower_ = lb.astype(np.float64)
        model.lp_.col_upper_ = ub.astype(np.float64)
        model.lp_.row_lower_ = alb.astype(np.float64)
        model.lp_.row_upper_ = aub.astype(np.float64)
        model.lp_.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        model.lp_.a_matrix_.start_ = a.indptr
        model.lp_.a_matrix_.index_ = a.indices
        model.lp_.a_matrix_.value_ = a.data
        model.hessian_.dim_ = n
        model.hessian_.start_ = q.indptr
        model.hessian_.index_ = q.indices
        model.hessian_.value_ = q.data

        qp = highspy.Highs()
        qp.setOptionValue("output_flag", bool(debug))
        qp.passModel(model)

        run_status = qp.run()
        model_status = qp.getModelStatus()
        model_status_str = qp.modelStatusToString(model_status)

        # проверка статуса решения
        if "Optimal" not in model_status_str:
            raise ValueError(
                "HiGHS QP (модиф.) не нашел оптимальное решение. "
                f"Статус: {model_status_str}"
            )

        solution = qp.getSolution()
        x = np.array(solution.col_value, dtype=float)
        if x.size != n:
            raise ValueError("HiGHS QP (модиф.) не вернул корректный вектор решения.")

        # контроль уравнения баланса заряд-разряд + собственные нужды
        balance_check = float(np.sum(x[m : 2 * m]) + np.sum(self.standby_load))

        if abs(balance_check) >= 0.001:
            print(
                f"Предупреждение: баланс заряд-разряд нарушен на {balance_check:.3f} МВтч"
            )

        eens_energy_available = x[0:m]
        eens_load = np.zeros(m)
        for i in range(m):
            eens_load[i] = (
                (1.0 if x[i + m] > 0 else 1.0 / self.pin_loss_factor) * x[i + m]
            )

        # формирование результата
        result_payload = {
            "eess_load": eens_load,
            "soc_energy": eens_energy_available,
            "deficit": x[m * 2],
            "reserve": x[m * 2 + 1] / self.pin_loss_factor,
        }
        if debug:
            result_payload["debug_info"] = _collect_highs_qp_debug_modified(
                mode="calculate_dispatch_schedule_qp_highs_modified",
                c=c,
                Q=q.toarray(),
                A=a.toarray(),
                row_lower=alb,
                row_upper=aub,
                lb=lb,
                ub=ub,
                solver_status=run_status,
                model_status=model_status,
                model_status_str=model_status_str,
                alpha_d=alpha_d,
                standby_load_mw=self.standby_load_mw,
                model=model,
            )
        return result_payload
