"""
Тестовый скрипт для проверки QP алгоритма расчета диспетчерского графика СНЭЭ
"""
import sys
import os
import numpy as np

# Добавляем путь к директории backend
sys.path.append(os.path.dirname(__file__))

from energy_storage_calculator import EnergyStorageCalculator_qp

def test_qp_dispatch_schedule():
    """
    Тестирование QP алгоритма расчета диспетчерского графика
    """
    print("=" * 80)
    print("Тестирование QP алгоритма расчета диспетчерского графика СНЭЭ".center(80))
    print("=" * 80)
    
    # Тестовые данные из VB кода
    load_profile = [
        27, 38, 84, 137.5, 21.3, -115.2, -166.2, -185.6, 
        -130.3, -48.21, 37.5, 152, 103, 175, 99, 49, 
        -47, 7, -130, -176, -117, -222, -205, -166
    ]
    
    # Параметры СНЭЭ (используем значения, близкие к ожидаемым оптимальным)
    dblNIn = 200    # входная мощность (МВт)
    dblNOut = 180   # выходная мощность (МВт)
    dblCapacity = 500  # емкость (МВтч)
    efficiency = 0.95
    
    print("\nИсходные данные:")
    print("-" * 80)
    print(f"Профиль баланса мощности (24 часа):")
    for i in range(0, 24, 6):
        hour_range = f"{i:02d}:00 - {i+5:02d}:00"
        values = ", ".join([f"{load_profile[j]:7.1f}" for j in range(i, min(i+6, 24))])
        print(f"  {hour_range}: [{values}]")
    
    print(f"\nПараметры СНЭЭ:")
    print(f"  Номинальная входная мощность (Nin):  {dblNIn} МВт")
    print(f"  Номинальная выходная мощность (Nout): {dblNOut} МВт")
    print(f"  Емкость батареи (C):                  {dblCapacity} МВтч")
    print(f"  КПД цикла (η):                        {efficiency}")
    
    # Создание калькулятора с поддержкой асимметричных мощностей
    print("\n" + "=" * 80)
    print("Запуск QP оптимизации...")
    print("-" * 80)
    
    try:
        calculator = EnergyStorageCalculator_qp(
            rated_power_mw=dblNOut,  # Для обратной совместимости
            rated_capacity_mwh=dblCapacity,
            efficiency=efficiency,
            rated_power_in_mw=dblNIn,
            rated_power_out_mw=dblNOut
        )
        
        # Расчет диспетчерского графика
        eess_schedule = calculator.calculate_dispatch_schedule_qp(load_profile)
        
        # Получение summary с дополнительными параметрами QP
        summary = calculator.get_summary(load_profile, eess_schedule)
        
        print("✓ Расчет завершен успешно!\n")
        
        # Вывод результатов
        print("=" * 80)
        print("РЕЗУЛЬТАТЫ РАСЧЕТА".center(80))
        print("=" * 80)
        
        print("\n1. Оптимальный диспетчерский график СНЭЭ (dblEENSLoad):")
        print("-" * 80)
        print("Час   | Баланс  | График СНЭЭ | Результат")
        print("      | системы | (+ разряд,  | баланса")
        print("      | (МВт)   | - заряд)    | (МВт)")
        print("-" * 80)
        
        resulting_balance = np.array(load_profile) + eess_schedule
        
        for i in range(24):
            status = ""
            if eess_schedule[i] > 0.01:
                status = " (разряд)"
            elif eess_schedule[i] < -0.01:
                status = " (заряд)"
            else:
                status = " (—)"
            
            print(f"{i:02d}:00 | {load_profile[i]:7.1f} | {eess_schedule[i]:10.2f}{status:10s} | {resulting_balance[i]:7.1f}")
        
        print("\n2. Сводная статистика:")
        print("-" * 80)
        print(f"Суммарный заряд:            {summary['total_charge_mwh']:.2f} МВтч")
        print(f"Суммарный разряд:           {summary['total_discharge_mwh']:.2f} МВтч")
        print(f"Макс. мощность заряда:      {summary['max_charge_power_mw']:.2f} МВт")
        print(f"Макс. мощность разряда:     {summary['max_discharge_power_mw']:.2f} МВт")
        
        print(f"\nДефицит до СНЭЭ:            {summary['deficit_before_mwh']:.2f} МВтч")
        print(f"Дефицит после СНЭЭ:         {summary['deficit_after_mwh']:.2f} МВтч")
        print(f"Покрыто дефицита:           {summary['deficit_covered_mwh']:.2f} МВтч ({summary['deficit_coverage_percent']:.1f}%)")
        
        print(f"\nИзбыток до СНЭЭ:            {summary['surplus_before_mwh']:.2f} МВтч")
        print(f"Избыток после СНЭЭ:         {summary['surplus_after_mwh']:.2f} МВтч")
        print(f"Использовано избытка:       {summary['surplus_utilized_mwh']:.2f} МВтч ({summary['surplus_utilization_percent']:.1f}%)")
        
        print(f"\nМакс. дефицит результата:   {summary['resulting_max_deficit_mw']:.2f} МВт")
        print(f"Макс. избыток результата:   {summary['resulting_max_surplus_mw']:.2f} МВт")
        
        # Вывод параметров QP, если доступны
        if 'qp_deficit_max_mw' in summary:
            print("\n3. Параметры из QP решения:")
            print("-" * 80)
            print(f"Максимальный дефицит (Dmax): {summary['qp_deficit_max_mw']:.2f} МВт")
            print(f"Максимальный резерв (Rmax):  {summary['qp_reserve_max_mw']:.2f} МВт")
        
        # Проверка баланса
        print("\n4. Проверка баланса:")
        print("-" * 80)
        charge_sum = -np.sum(eess_schedule[eess_schedule < 0])
        discharge_sum = np.sum(eess_schedule[eess_schedule > 0])
        balance_error = abs(charge_sum - discharge_sum)
        
        print(f"Суммарный заряд:   {charge_sum:.4f} МВтч")
        print(f"Суммарный разряд:  {discharge_sum:.4f} МВтч")
        print(f"Небаланс:          {balance_error:.6f} МВтч")
        
        if balance_error < 0.1:
            print("✓ Баланс соблюден")
        else:
            print("⚠ Значительный небаланс!")
        
        # Дополнительная информация из QP решения
        if hasattr(calculator, '_last_qp_solution'):
            qp_sol = calculator._last_qp_solution
            
            print("\n5. Детальная информация из QP решения:")
            print("-" * 80)
            
            print("\nУровень энергии в батарее (dL):")
            energy_levels = qp_sol['energy_available']
            for i in range(0, 24, 6):
                values = ", ".join([f"{energy_levels[j]:6.1f}" for j in range(i, min(i+6, 24))])
                print(f"  Часы {i:02d}-{min(i+5, 23):02d}: [{values}]")
            
            print(f"\nМакс. уровень энергии: {np.max(energy_levels):.2f} МВтч")
            print(f"Мин. уровень энергии:  {np.min(energy_levels):.2f} МВтч")
        
        print("\n" + "=" * 80)
        print("ПРИМЕЧАНИЕ".center(80))
        print("=" * 80)
        print("Для проверки корректности сравните эти значения с результатами".center(80))
        print("из Excel файла (ячейки B10:Y10 - уровень энергии, B11:Y11 - график нагрузки,".center(80))
        print("B13 - дефицит, B14 - резерв)".center(80))
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Ошибка при расчете: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_qp_dispatch_schedule()
    sys.exit(0 if success else 1)

