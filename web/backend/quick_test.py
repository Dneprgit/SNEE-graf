import numpy as np
from energy_storage_calculator import EnergyStorageCalculator_qp

# Быстрый тест
load = [27, 38, 84, 137.5, 21.3, -115.2, -166.2, -185.6, -130.3, -48.21, 37.5, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166]

calc = EnergyStorageCalculator_qp(200, 500, 0.95, 200, 180)
result = calc.calculate_dispatch_schedule_qp(load)

print("Success! График СНЭЭ:")
print(result)
print(f"\nСумма заряда: {-np.sum(result[result < 0]):.2f}")
print(f"Сумма разряда: {np.sum(result[result > 0]):.2f}")

if hasattr(calc, '_last_qp_solution'):
    print(f"\nDmax: {calc._last_qp_solution['deficit_max']:.2f} МВт")
    print(f"Rmax: {calc._last_qp_solution['reserve_max']:.2f} МВт")

