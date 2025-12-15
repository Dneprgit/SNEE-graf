"""Быстрый тест QP алгоритма"""
from energy_storage_calculator import calculate_optimal_parameters_qp

# Тестовые данные
load = [27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
        37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166]

result = calculate_optimal_parameters_qp(load, 0.95)

print("РЕЗУЛЬТАТЫ:")
print(f"Nin: {result['nin']}")
print(f"Nout: {result['nout']}")
print(f"Capacity: {result['capacity']}")
print(f"Deficit: {result['deficit']}")

