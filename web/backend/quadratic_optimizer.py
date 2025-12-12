"""
Модуль квадратичной оптимизации с использованием alglib-cpython
Обертка над alglib IPM solver для решения задач квадратичного программирования
"""
import sys
import os
import numpy as np

# Добавить путь к alglib-cpython
alglib_path = os.path.join(os.path.dirname(__file__), '../alglib-cpython')
if alglib_path not in sys.path:
    sys.path.insert(0, alglib_path)

try:
    import xalglib
except ImportError as e:
    raise ImportError(f"Не удалось импортировать xalglib. Убедитесь, что alglib-cpython установлен: {e}")


def solve_qp_problem(n: int, k: int, A: np.ndarray, b: np.ndarray, 
                     C: np.ndarray, cl: np.ndarray, cu: np.ndarray,
                     lb: np.ndarray, ub: np.ndarray, s: np.ndarray, x0: np.ndarray):
    """
    Решение задачи квадратичной оптимизации с IPM методом
    
    Минимизирует: F(x) = 0.5*x'*A*x + b'*x
    
    При ограничениях:
        lb <= x <= ub           (box constraints)
        cl <= C'*x <= cu        (linear constraints)
    
    Args:
        n: Размерность задачи (количество переменных)
        k: Количество линейных ограничений
        A: Матрица квадратичного терма (n×n), должна быть симметричной
        b: Вектор линейного терма (n)
        C: Матрица линейных ограничений (k×n) - TRANSPOSE of VB format!
        cl: Нижние границы линейных ограничений (k)
        cu: Верхние границы линейных ограничений (k)
        lb: Нижние границы переменных (n)
        ub: Верхние границы переменных (n)
        s: Масштаб переменных (n)
        x0: Начальное приближение (n)
    
    Returns:
        Tuple[np.ndarray, int]: (решение x, код завершения)
        
    Коды завершения:
        -9: failure of automatic scale evaluation
        -5: inappropriate solver was used
        -4: function is unbounded from below
        -3: inconsistent constraints
        -2: IPM solver has difficulty finding feasible point
         1: function change is small enough
         2: X(k+1)-X(k) is small enough
         4: gradient is small enough
         5: too many iterations
         7: stopping conditions too stringent
         8: user requested termination
    """
    # Проверка размерностей
    assert A.shape == (n, n), f"A должна быть {n}×{n}, получена {A.shape}"
    assert len(b) == n, f"b должен иметь длину {n}, получена {len(b)}"
    assert C.shape == (k, n), f"C должна быть {k}×{n}, получена {C.shape}"
    assert len(cl) == k, f"cl должен иметь длину {k}, получена {len(cl)}"
    assert len(cu) == k, f"cu должен иметь длину {k}, получена {len(cu)}"
    assert len(lb) == n, f"lb должен иметь длину {n}, получена {len(lb)}"
    assert len(ub) == n, f"ub должен иметь длину {n}, получена {len(ub)}"
    assert len(s) == n, f"s должен иметь длину {n}, получена {len(s)}"
    assert len(x0) == n, f"x0 должен иметь длину {n}, получена {len(x0)}"
    
    # Преобразование массивов в списки для alglib
    A_list = A.tolist() if isinstance(A, np.ndarray) else A
    b_list = b.tolist() if isinstance(b, np.ndarray) else b
    C_list = C.tolist() if isinstance(C, np.ndarray) else C
    cl_list = cl.tolist() if isinstance(cl, np.ndarray) else cl
    cu_list = cu.tolist() if isinstance(cu, np.ndarray) else cu
    lb_list = lb.tolist() if isinstance(lb, np.ndarray) else lb
    ub_list = ub.tolist() if isinstance(ub, np.ndarray) else ub
    s_list = s.tolist() if isinstance(s, np.ndarray) else s
    x0_list = x0.tolist() if isinstance(x0, np.ndarray) else x0
    
    # Заменить inf на значения, которые понимает alglib
    MAX_REAL = 1.0e+300
    
    cl_list = [MAX_REAL if x >= 1.0e+300 else (-MAX_REAL if x <= -1.0e+300 else x) for x in cl_list]
    cu_list = [MAX_REAL if x >= 1.0e+300 else (-MAX_REAL if x <= -1.0e+300 else x) for x in cu_list]
    lb_list = [MAX_REAL if x >= 1.0e+300 else (-MAX_REAL if x <= -1.0e+300 else x) for x in lb_list]
    ub_list = [MAX_REAL if x >= 1.0e+300 else (-MAX_REAL if x <= -1.0e+300 else x) for x in ub_list]
    
    try:
        # Создать minqp state
        state = xalglib.minqpcreate(n)
        
        # Установить квадратичный терм (A должна быть симметричной, isupper=True)
        xalglib.minqpsetquadraticterm(state, A_list, True)
        
        # Установить линейный терм
        xalglib.minqpsetlinearterm(state, b_list)
        
        # Установить начальную точку
        xalglib.minqpsetstartingpoint(state, x0_list)
        
        # Установить границы переменных
        xalglib.minqpsetbc(state, lb_list, ub_list)
        
        # Установить линейные ограничения (двусторонние)
        xalglib.minqpsetlc2dense(state, C_list, cl_list, cu_list, k)
        
        # Установить масштаб переменных
        xalglib.minqpsetscale(state, s_list)
        
        # Выбрать IPM solver (Dense IPM для плотных матриц)
        # eps=0.0 означает автоматический выбор точности
        xalglib.minqpsetalgodenseipm(state, 0.0)
        
        # Оптимизировать
        xalglib.minqpoptimize(state)
        
        # Получить результаты
        x, rep = xalglib.minqpresults(state)
        
        # Преобразовать результат в numpy массив
        x_array = np.array(x)
        termination_type = rep.terminationtype
        
        return x_array, termination_type
        
    except Exception as e:
        raise RuntimeError(f"Ошибка при решении задачи квадратичной оптимизации: {e}")


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
        -2: (False, "IPM solver has difficulty finding feasible point"),
        1: (True, "Function change is small enough"),
        2: (True, "X(k+1)-X(k) is small enough"),
        4: (True, "Gradient is small enough"),
        5: (True, "Too many iterations (but solution may be acceptable)"),
        7: (True, "Stopping conditions too stringent (solution acceptable)"),
        8: (True, "User requested termination"),
    }
    
    success, message = codes.get(code, (False, f"Unknown termination code: {code}"))
    return success, message

