"""
Модуль квадратичной оптимизации с использованием QuickQP.dll
Обертка над C++ библиотекой для решения задач квадратичного программирования

ВАЖНО: QuickQP.dll использует SAFEARRAY из VB, что сложно для ctypes.
Альтернативное решение: использовать alglib C++ напрямую через компиляцию или
использовать чистый Python solver (scipy.optimize.minimize с method='trust-constr')
"""
import sys
import os
import numpy as np
from typing import Tuple
from scipy.optimize import minimize, LinearConstraint, Bounds


def solve_qp_problem_scipy(n: int, k: int, A: np.ndarray, b: np.ndarray, 
                          C: np.ndarray, cl: np.ndarray, cu: np.ndarray,
                          lb: np.ndarray, ub: np.ndarray, s: np.ndarray, x0: np.ndarray):
    """
    Решение задачи квадратичной оптимизации с scipy
    
    Минимизирует: F(x) = 0.5*x'*A*x + b'*x
    
    При ограничениях:
        lb <= x <= ub           (box constraints)
        cl <= C'*x <= cu        (linear constraints)
    
    Args:
        n: Размерность задачи
        k: Количество линейных ограничений
        A: Матрица квадратичного терма (n×n)
        b: Вектор линейного терма (n)
        C: Матрица линейных ограничений (k×n)
        cl: Нижние границы линейных ограничений (k)
        cu: Верхние границы линейных ограничений (k)
        lb: Нижние границы переменных (n)
        ub: Верхние границы переменных (n)
        s: Масштаб переменных (n) - используется для x0
        x0: Начальное приближение (n)
    
    Returns:
        Tuple[np.ndarray, int]: (решение x, код завершения)
    """
    
    # Целевая функция: F(x) = 0.5*x'*A*x + b'*x
    def objective(x):
        return 0.5 * x.dot(A.dot(x)) + b.dot(x)
    
    # Градиент: dF/dx = A*x + b
    def gradient(x):
        return A.dot(x) + b
    
    # Гессиан: d²F/dx² = A
    def hessian(x):
        return A
    
    # Заменить inf на большие числа для scipy
    MAX_BOUND = 1e15
    lb_bounded = np.where(lb < -1e100, -MAX_BOUND, lb)
    ub_bounded = np.where(ub > 1e100, MAX_BOUND, ub)
    cl_bounded = np.where(cl < -1e100, -MAX_BOUND, cl)
    cu_bounded = np.where(cu > 1e100, MAX_BOUND, cu)
    
    # Ограничения
    bounds = Bounds(lb_bounded, ub_bounded)
    
    # Линейные ограничения: cl <= C @ x <= cu
    if k > 0:
        linear_constraint = LinearConstraint(C, cl_bounded, cu_bounded)
        constraints = [linear_constraint]
    else:
        constraints = []
    
    # Решение задачи оптимизации
    try:
        result = minimize(
            objective,
            x0,
            method='trust-constr',
            jac=gradient,
            hess=hessian,
            bounds=bounds,
            constraints=constraints,
            options={
                'maxiter': 1000,
                'verbose': 0,
                'gtol': 1e-6,
                'xtol': 1e-8,
            }
        )
        
        # Преобразование статуса scipy в коды alglib
        if result.success:
            if result.nit < 10:
                termination_code = 2  # X(k+1)-X(k) is small enough
            elif result.optimality < 1e-4:
                termination_code = 4  # gradient is small enough
            else:
                termination_code = 1  # function change is small enough
        else:
            if 'infeasible' in result.message.lower():
                termination_code = -3  # inconsistent constraints
            elif 'unbounded' in result.message.lower():
                termination_code = -4  # unbounded from below
            else:
                termination_code = -2  # difficulty finding feasible point
        
        return result.x, termination_code
        
    except Exception as e:
        print(f"Ошибка оптимизации: {e}")
        return x0, -2


# Основная функция для совместимости
def solve_qp_problem(n: int, k: int, A: np.ndarray, b: np.ndarray, 
                     C: np.ndarray, cl: np.ndarray, cu: np.ndarray,
                     lb: np.ndarray, ub: np.ndarray, s: np.ndarray, x0: np.ndarray):
    """
    Решение задачи квадратичной оптимизации
    Использует scipy.optimize.minimize с методом trust-constr
    """
    return solve_qp_problem_scipy(n, k, A, b, C, cl, cu, lb, ub, s, x0)


def check_termination_code(code: int) -> tuple[bool, str]:
    """
    Проверка кода завершения оптимизации
    
    Args:
        code: Код завершения
    
    Returns:
        Tuple[bool, str]: (успешно ли завершение, описание)
    """
    codes = {
        -9: (False, "Failure of automatic scale evaluation"),
        -5: (False, "Inappropriate solver was used"),
        -4: (False, "Function is unbounded from below"),
        -3: (False, "Inconsistent constraints"),
        -2: (False, "Difficulty finding feasible point"),
        1: (True, "Function change is small enough"),
        2: (True, "X(k+1)-X(k) is small enough"),
        4: (True, "Gradient is small enough"),
        5: (True, "Too many iterations (but solution may be acceptable)"),
        7: (True, "Stopping conditions too stringent (solution acceptable)"),
        8: (True, "User requested termination"),
    }
    
    success, message = codes.get(code, (False, f"Unknown termination code: {code}"))
    return success, message
