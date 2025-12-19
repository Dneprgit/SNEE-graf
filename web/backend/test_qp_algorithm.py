"""
Тестовый скрипт для проверки реализации алгоритма квадратичной оптимизации
Сравнение результатов Python ALGLIB с результатами из VB кода
"""

from energy_storage_calculator_ import calculate_optimal_parameters_qp

# Тестовые данные - профиль баланса мощности из примера
load_profile = [
    1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
    -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
    -638, -370, 59, 963
]

# КПД системы
efficiency = 0.95

print("=" * 80)
print("Тестирование алгоритма квадратичной оптимизации (QP)")
print("=" * 80)
print("\nИсходные данные:")
print(f"Профиль баланса мощности (24 часа): {load_profile}")
print(f"КПД цикла: {efficiency}")
print("\nЗапуск расчета оптимальных параметров...")
print("-" * 80)

try:
    result = calculate_optimal_parameters_qp(load_profile, efficiency)
    
    print("\n✓ Расчет завершен успешно!")
    print("\nОптимальные параметры СНЭЭ (алгоритм QP):")
    print("=" * 80)
    print(f"Номинальная входная мощность (Nin):  {result['optimal_power_in_mw']:.2f} МВт")
    print(f"Номинальная выходная мощность (Nout): {result['optimal_power_out_mw']:.2f} МВт")
    print(f"Емкость батареи (C):                  {result['optimal_capacity_mwh']:.2f} МВтч")
    print(f"Дефицит мощности (Dmax):              {result['deficit_mw']:.2f} МВт")
    
    print("\nДополнительные рассчитанные параметры:")
    print("=" * 80)
    
    # Рассчитываем дополнительные параметры
    discharge_time = result['optimal_capacity_mwh'] / result['optimal_power_out_mw']
    charge_energy = result['optimal_capacity_mwh'] / efficiency
    charge_time = charge_energy / result['optimal_power_in_mw']
    
    print(f"Фактическое время разряда:            {discharge_time:.2f} ч")
    print(f"Энергия, затраченная на заряд:        {charge_energy:.2f} МВтч")
    print(f"Фактическое время заряда:             {charge_time:.2f} ч")
    
    print("\n" + "=" * 80)
    print("ПРИМЕЧАНИЕ:")
    print("Для проверки корректности результатов сравните эти значения")
    print("с результатами из Excel файла (ячейки B2, B3, B4, B13)")
    print("=" * 80)
    
except ImportError as e:
    print(f"\n✗ Ошибка импорта: {e}")
    print("\nУстановите необходимые библиотеки:")
    print("  pip install scipy>=1.10.0")
    
except Exception as e:
    print(f"\n✗ Ошибка при расчете: {e}")
    import traceback
    traceback.print_exc()

print("\nТестирование завершено.")

