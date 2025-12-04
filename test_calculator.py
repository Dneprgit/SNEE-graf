"""
Тестовый скрипт для проверки расчета диспетчерского графика СНЭЭ
"""
from energy_storage_calculator import EnergyStorageCalculator
from data_manager import DataManager
import numpy as np


def test_default_profile():
    """Тест с профилем по умолчанию"""
    print("=" * 70)
    print("ТЕСТ: Расчет диспетчерского графика СНЭЭ")
    print("=" * 70)
    print()
    
    # Исходные данные
    load_profile = DataManager.get_default_profile()
    rated_power = 500  # МВт
    rated_capacity = 2000  # МВтч
    efficiency = 0.95
    
    print("ИСХОДНЫЕ ДАННЫЕ:")
    print(f"  Мощность инвертора: {rated_power} МВт")
    print(f"  Емкость батареи: {rated_capacity} МВтч")
    print(f"  КПД трансформации: {efficiency}")
    print()
    
    print("Профиль баланса мощности (24 часа):")
    for i in range(0, 24, 6):
        hours_str = " | ".join([f"{i+j+1:2d}ч" for j in range(6)])
        values_str = " | ".join([f"{load_profile[i+j]:6.0f}" for j in range(6)])
        print(f"  {hours_str}")
        print(f"  {values_str} МВт")
        print()
    
    # Расчет
    print("-" * 70)
    calculator = EnergyStorageCalculator(rated_power, rated_capacity, efficiency)
    eess_schedule = calculator.calculate_dispatch_schedule(load_profile)
    summary = calculator.get_summary(load_profile, eess_schedule)
    
    print("РЕЗУЛЬТАТЫ РАСЧЕТА:")
    print()
    print("График работы СНЭЭ (+ разряд, - заряд):")
    for i in range(0, 24, 6):
        hours_str = " | ".join([f"{i+j+1:2d}ч" for j in range(6)])
        values_str = " | ".join([f"{eess_schedule[i+j]:6.1f}" for j in range(6)])
        print(f"  {hours_str}")
        print(f"  {values_str} МВт")
        print()
    
    print("-" * 70)
    print("СВОДНАЯ ИНФОРМАЦИЯ:")
    print()
    print("Энергетические показатели:")
    print(f"  Суммарный заряд:              {summary['total_charge_mwh']:>8.2f} МВтч")
    print(f"  Суммарный разряд:             {summary['total_discharge_mwh']:>8.2f} МВтч")
    print(f"  Макс. мощность заряда:        {summary['max_charge_power_mw']:>8.2f} МВт")
    print(f"  Макс. мощность разряда:       {summary['max_discharge_power_mw']:>8.2f} МВт")
    print()
    
    print("Покрытие дефицитов:")
    print(f"  Дефицит до СНЭЭ:              {summary['deficit_before_mwh']:>8.2f} МВтч")
    print(f"  Дефицит после СНЭЭ:           {summary['deficit_after_mwh']:>8.2f} МВтч")
    print(f"  Покрытый дефицит:             {summary['deficit_covered_mwh']:>8.2f} МВтч")
    print(f"  Процент покрытия:             {summary['deficit_coverage_percent']:>8.1f} %")
    print()
    
    print("Использование избытков:")
    print(f"  Избыток до СНЭЭ:              {summary['surplus_before_mwh']:>8.2f} МВтч")
    print(f"  Избыток после СНЭЭ:           {summary['surplus_after_mwh']:>8.2f} МВтч")
    print(f"  Использованный избыток:       {summary['surplus_utilized_mwh']:>8.2f} МВтч")
    print(f"  Процент использования:        {summary['surplus_utilization_percent']:>8.1f} %")
    print()
    
    print("Результирующие показатели:")
    print(f"  Макс. дефицит (после СНЭЭ):   {summary['resulting_max_deficit_mw']:>8.2f} МВт")
    print(f"  Макс. избыток (после СНЭЭ):   {summary['resulting_max_surplus_mw']:>8.2f} МВт")
    print()
    
    # Проверка баланса энергии
    balance = np.sum(eess_schedule)
    print(f"Энергетический баланс за сутки: {balance:.2f} МВтч")
    if abs(balance) < 0.1:
        print("✓ Баланс сходится (заряд = разряд)")
    else:
        print("✗ ВНИМАНИЕ: Баланс не сходится!")
    
    print()
    print("=" * 70)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 70)


def test_edge_cases():
    """Тест граничных случаев"""
    print("\nТЕСТ ГРАНИЧНЫХ СЛУЧАЕВ:")
    print("-" * 70)
    
    # Случай 1: Только избытки
    print("\n1. Профиль только с избытками:")
    load_profile = [100] * 24
    calculator = EnergyStorageCalculator(500, 2000, 0.95)
    eess = calculator.calculate_dispatch_schedule(load_profile)
    print(f"   Суммарная работа СНЭЭ: {np.sum(eess):.2f} МВтч")
    print(f"   Ожидается: 0 (нет разряда)")
    
    # Случай 2: Только дефициты
    print("\n2. Профиль только с дефицитами:")
    load_profile = [-100] * 24
    calculator = EnergyStorageCalculator(500, 2000, 0.95)
    eess = calculator.calculate_dispatch_schedule(load_profile)
    print(f"   Суммарная работа СНЭЭ: {np.sum(eess):.2f} МВтч")
    print(f"   Ожидается: 0 (нет заряда)")
    
    # Случай 3: Малая мощность
    print("\n3. Мощность инвертора 50 МВт (маленькая):")
    load_profile = DataManager.get_default_profile()
    calculator = EnergyStorageCalculator(50, 2000, 0.95)
    eess = calculator.calculate_dispatch_schedule(load_profile)
    summary = calculator.get_summary(load_profile, eess)
    print(f"   Покрытие дефицита: {summary['deficit_coverage_percent']:.1f}%")
    
    # Случай 4: Малая емкость
    print("\n4. Емкость батареи 100 МВтч (маленькая):")
    calculator = EnergyStorageCalculator(500, 100, 0.95)
    eess = calculator.calculate_dispatch_schedule(load_profile)
    summary = calculator.get_summary(load_profile, eess)
    print(f"   Покрытие дефицита: {summary['deficit_coverage_percent']:.1f}%")
    
    # Случай 5: Большая мощность и емкость
    print("\n5. Мощность 2000 МВт, емкость 10000 МВтч (большие):")
    calculator = EnergyStorageCalculator(2000, 10000, 0.95)
    eess = calculator.calculate_dispatch_schedule(load_profile)
    summary = calculator.get_summary(load_profile, eess)
    print(f"   Покрытие дефицита: {summary['deficit_coverage_percent']:.1f}%")
    print(f"   Использование избытка: {summary['surplus_utilization_percent']:.1f}%")
    
    print("\n" + "-" * 70)
    print("ГРАНИЧНЫЕ ТЕСТЫ ЗАВЕРШЕНЫ")


if __name__ == '__main__':
    test_default_profile()
    test_edge_cases()

