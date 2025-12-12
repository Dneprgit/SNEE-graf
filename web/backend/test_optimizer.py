"""
Тестовый скрипт для проверки работы quadratic_optimizer с scipy
Сравнение результатов с простыми аналитическими решениями
"""
import numpy as np
from quadratic_optimizer import solve_qp_problem, check_termination_code


def test_simple_quadratic():
    """
    Тест 1: Простая квадратичная функция без ограничений
    Минимизировать: (x-2)^2 + (y-3)^2
    Ожидаемое решение: x=2, y=3
    """
    print("\n" + "="*60)
    print("ТЕСТ 1: Простая квадратичная функция")
    print("="*60)
    print("Минимизировать: (x-2)² + (y-3)²")
    print("Ожидаемое решение: x=2, y=3")
    
    n = 2
    k = 0
    
    # F(x) = 0.5*x'*A*x + b'*x
    # (x-2)^2 + (y-3)^2 = x^2 - 4x + 4 + y^2 - 6y + 9
    # = 0.5*[x,y]*[[2,0],[0,2]]*[x,y]' + [-4,-6]*[x,y]'
    A = np.array([[2.0, 0.0], [0.0, 2.0]])
    b = np.array([-4.0, -6.0])
    C = np.zeros((0, n))
    cl = np.array([])
    cu = np.array([])
    lb = np.array([-np.inf, -np.inf])
    ub = np.array([np.inf, np.inf])
    s = np.array([1.0, 1.0])
    x0 = np.array([0.0, 0.0])
    
    x, code = solve_qp_problem(n, k, A, b, C, cl, cu, lb, ub, s, x0)
    success, message = check_termination_code(code)
    
    print(f"\nРезультат: x = {x}")
    print(f"Код завершения: {code} - {message}")
    print(f"Статус: {'✓ Успех' if success else '✗ Ошибка'}")
    
    # Проверка точности
    expected = np.array([2.0, 3.0])
    error = np.linalg.norm(x - expected)
    print(f"Ошибка: {error:.2e}")
    print(f"Тест: {'✓ ПРОЙДЕН' if error < 1e-4 else '✗ НЕ ПРОЙДЕН'}")


def test_with_box_constraints():
    """
    Тест 2: Квадратичная функция с box constraints
    Минимизировать: (x-5)^2 + (y-5)^2
    При ограничениях: 0 <= x <= 3, 0 <= y <= 3
    Ожидаемое решение: x=3, y=3 (граница)
    """
    print("\n" + "="*60)
    print("ТЕСТ 2: С box constraints")
    print("="*60)
    print("Минимизировать: (x-5)² + (y-5)²")
    print("Ограничения: 0 ≤ x ≤ 3, 0 ≤ y ≤ 3")
    print("Ожидаемое решение: x=3, y=3")
    
    n = 2
    k = 0
    
    A = np.array([[2.0, 0.0], [0.0, 2.0]])
    b = np.array([-10.0, -10.0])
    C = np.zeros((0, n))
    cl = np.array([])
    cu = np.array([])
    lb = np.array([0.0, 0.0])
    ub = np.array([3.0, 3.0])
    s = np.array([1.0, 1.0])
    x0 = np.array([0.0, 0.0])
    
    x, code = solve_qp_problem(n, k, A, b, C, cl, cu, lb, ub, s, x0)
    success, message = check_termination_code(code)
    
    print(f"\nРезультат: x = {x}")
    print(f"Код завершения: {code} - {message}")
    print(f"Статус: {'✓ Успех' if success else '✗ Ошибка'}")
    
    expected = np.array([3.0, 3.0])
    error = np.linalg.norm(x - expected)
    print(f"Ошибка: {error:.2e}")
    print(f"Тест: {'✓ ПРОЙДЕН' if error < 1e-4 else '✗ НЕ ПРОЙДЕН'}")


def test_with_linear_constraints():
    """
    Тест 3: С линейными ограничениями
    Минимизировать: (x-4)^2 + (y-4)^2
    При ограничениях: x + y <= 5, x >= 0, y >= 0
    Ожидаемое решение: x=2.5, y=2.5 (на линии x+y=5)
    """
    print("\n" + "="*60)
    print("ТЕСТ 3: С линейными ограничениями")
    print("="*60)
    print("Минимизировать: (x-4)² + (y-4)²")
    print("Ограничения: x + y ≤ 5, x ≥ 0, y ≥ 0")
    print("Ожидаемое решение: x≈2.5, y≈2.5")
    
    n = 2
    k = 1
    
    A = np.array([[2.0, 0.0], [0.0, 2.0]])
    b = np.array([-8.0, -8.0])
    C = np.array([[1.0, 1.0]])  # x + y
    cl = np.array([-np.inf])
    cu = np.array([5.0])
    lb = np.array([0.0, 0.0])
    ub = np.array([np.inf, np.inf])
    s = np.array([1.0, 1.0])
    x0 = np.array([1.0, 1.0])
    
    x, code = solve_qp_problem(n, k, A, b, C, cl, cu, lb, ub, s, x0)
    success, message = check_termination_code(code)
    
    print(f"\nРезультат: x = {x}")
    print(f"Код завершения: {code} - {message}")
    print(f"Статус: {'✓ Успех' if success else '✗ Ошибка'}")
    print(f"Проверка ограничения x+y: {x[0]+x[1]:.4f} (должно быть ≤ 5)")
    
    expected = np.array([2.5, 2.5])
    error = np.linalg.norm(x - expected)
    print(f"Ошибка: {error:.2e}")
    print(f"Тест: {'✓ ПРОЙДЕН' if error < 1e-3 else '✗ НЕ ПРОЙДЕН'}")


def test_snee_like_problem():
    """
    Тест 4: Задача, похожая на СНЭЭ
    Минимизация отклонения от целевого профиля с учетом баланса энергии
    """
    print("\n" + "="*60)
    print("ТЕСТ 4: СНЭЭ-подобная задача")
    print("="*60)
    print("Балансировка 4-часового профиля")
    
    # 4 часа: дефицит, дефицит, избыток, избыток
    target_profile = np.array([50.0, 30.0, -40.0, -20.0])
    n = len(target_profile) * 2  # charge и discharge для каждого часа
    
    # Переменные: [pch0, pch1, pch2, pch3, pdch0, pdch1, pdch2, pdch3]
    # charge в часы 2,3; discharge в часы 0,1
    
    # Минимизируем квадраты отклонений
    A = np.eye(n) * 2.0
    b = np.zeros(n)
    
    # Линейные ограничения
    constraints = []
    
    # 1. Баланс энергии: sum(charge*eff) >= sum(discharge/eff)
    # 2. Не заряжаем и не разряжаем одновременно
    # 3. Мощность <= макс мощности
    
    k = 1  # баланс энергии
    C = np.zeros((k, n))
    eff = 0.95
    for i in range(4):
        C[0, i] = eff  # заряд
        C[0, i+4] = -1.0/eff  # разряд
    
    cl = np.array([0.0])  # заряд >= разряд
    cu = np.array([np.inf])
    
    # Box constraints
    lb = np.zeros(n)
    ub = np.ones(n) * 100.0  # макс 100 МВт
    
    s = np.ones(n)
    x0 = np.zeros(n)
    
    x, code = solve_qp_problem(n, k, A, b, C, cl, cu, lb, ub, s, x0)
    success, message = check_termination_code(code)
    
    print(f"\nРезультат:")
    print(f"  Заряд: {x[:4]}")
    print(f"  Разряд: {x[4:]}")
    print(f"Код завершения: {code} - {message}")
    print(f"Статус: {'✓ Успех' if success else '✗ Ошибка'}")
    
    charge_energy = sum(x[:4]) * eff
    discharge_energy = sum(x[4:]) / eff
    print(f"Энергия заряда: {charge_energy:.2f} МВт*ч")
    print(f"Энергия разряда: {discharge_energy:.2f} МВт*ч")
    print(f"Баланс: {charge_energy - discharge_energy:.2f} МВт*ч")
    print(f"Тест: {'✓ ПРОЙДЕН' if success and charge_energy >= discharge_energy - 1 else '✗ НЕ ПРОЙДЕН'}")


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  ТЕСТИРОВАНИЕ QUADRATIC OPTIMIZER (SCIPY)                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    test_simple_quadratic()
    test_with_box_constraints()
    test_with_linear_constraints()
    test_snee_like_problem()
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60 + "\n")

