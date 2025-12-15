"""
Тестовый скрипт для проверки корректности реализации QP алгоритма
"""
import numpy as np
from energy_storage_calculator import EnergyStorageCalculator_qp

def test_qp_optimization():
    """Тест QP оптимизации с реальными данными"""
    
    # Тестовые данные из примера (для QP полярность: + дефицит, - избыток)
    # Инвертируем знаки для QP варианта
    load_profile_original = [
        27, 38, 84, 137.5, 21.3, -115.2, -166.2, -185.6, -130.3, -48.21,
        37.5, 152, 103, 175, 99, 49, -47, 7, -130, -176,
        -117, -222, -205, -166
    ]
    
    # Для QP инвертируем знаки: положительное = дефицит
    load_profile_qp = [-x for x in load_profile_original]
    
    print("=" * 80)
    print("Тест QP оптимизации СНЭЭ")
    print("=" * 80)
    print()
    
    # Параметры СНЭЭ
    rated_power = 54.0  # МВт
    rated_capacity = 535.0  # МВтч
    efficiency = 0.95
    
    print(f"Параметры СНЭЭ:")
    print(f"  Мощность: {rated_power} МВт")
    print(f"  Емкость: {rated_capacity} МВтч")
    print(f"  КПД: {efficiency}")
    print()
    
    # Создание калькулятора
    calculator = EnergyStorageCalculator_qp(
        rated_power_mw=rated_power,
        rated_capacity_mwh=rated_capacity,
        efficiency=efficiency
    )
    
    try:
        # Расчет графика
        print("Запуск QP оптимизации...")
        result = calculator.calculate_dispatch_schedule_qp(load_profile_qp)
        
        eess_load = result['eess_load']
        soc_energy = result['soc_energy']
        deficit = result['deficit']
        reserve = result['reserve']
        
        print("✓ Оптимизация завершена успешно!")
        print()
        
        # 1. Проверка баланса заряд-разряд
        print("1. Проверка баланса заряд-разряд:")
        total_charge = -np.sum(eess_load[eess_load < 0])
        total_discharge = np.sum(eess_load[eess_load > 0])
        balance_diff = abs(total_charge - total_discharge)
        print(f"   Суммарный заряд: {total_charge:.3f} МВтч")
        print(f"   Суммарный разряд: {total_discharge:.3f} МВтч")
        print(f"   Разница: {balance_diff:.6f} МВтч")
        
        if balance_diff < 0.1:  # Допустимая погрешность
            print("   ✓ БАЛАНС СОБЛЮДЕН")
        else:
            print("   ✗ БАЛАНС НАРУШЕН!")
        print()
        
        # 2. Проверка ограничений SOC
        print("2. Проверка ограничений SOC (энергия в батарее):")
        min_soc = np.min(soc_energy)
        max_soc = np.max(soc_energy)
        print(f"   Минимум SOC: {min_soc:.2f} МВтч (должно быть >= 0)")
        print(f"   Максимум SOC: {max_soc:.2f} МВтч (должно быть <= {rated_capacity})")
        
        soc_valid = (min_soc >= -0.01) and (max_soc <= rated_capacity + 0.01)
        if soc_valid:
            print("   ✓ ОГРАНИЧЕНИЯ SOC СОБЛЮДЕНЫ")
        else:
            print("   ✗ ОГРАНИЧЕНИЯ SOC НАРУШЕНЫ!")
        print()
        
        # 3. Проверка результатов QP
        print("3. Результаты QP оптимизации:")
        print(f"   Дефицит мощности (Dmax): {deficit:.2f} МВт")
        print(f"   Резерв мощности (Rmax): {reserve:.2f} МВт")
        print()
        
        # 4. Проверка результирующего баланса
        print("4. Анализ результирующего баланса:")
        load_profile_array = np.array(load_profile_qp)
        resulting_balance = load_profile_array - eess_load
        
        # Для QP: положительное = дефицит
        remaining_deficit = np.sum(resulting_balance[resulting_balance > 0])
        remaining_surplus = -np.sum(resulting_balance[resulting_balance < 0])
        
        print(f"   Остаточный дефицит: {remaining_deficit:.2f} МВтч")
        print(f"   Остаточный избыток: {remaining_surplus:.2f} МВтч")
        print()
        
        # 5. Проверка мощностей
        print("5. Проверка мощностей:")
        max_charge_power = -np.min(eess_load)
        max_discharge_power = np.max(eess_load)
        print(f"   Макс. мощность заряда: {max_charge_power:.2f} МВт (лимит: {rated_power})")
        print(f"   Макс. мощность разряда: {max_discharge_power:.2f} МВт (лимит: {rated_power})")
        
        power_valid = (max_charge_power <= rated_power + 0.01) and (max_discharge_power <= rated_power + 0.01)
        if power_valid:
            print("   ✓ ОГРАНИЧЕНИЯ МОЩНОСТИ СОБЛЮДЕНЫ")
        else:
            print("   ✗ ОГРАНИЧЕНИЯ МОЩНОСТИ НАРУШЕНЫ!")
        print()
        
        # Итоговая статистика
        print("=" * 80)
        print("ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        
        summary = calculator.get_summary_qp(
            load_profile_qp,
            eess_load,
            deficit_mw=deficit,
            reserve_mw=reserve
        )
        
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        print()
        print("=" * 80)
        print("Тест завершен успешно!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_qp_optimization()
    exit(0 if success else 1)

