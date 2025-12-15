"""
Тестовый скрипт для проверки алгоритма квадратичной оптимизации (QP)
Использует тестовые данные из Project_context_QP.txt
"""
import sys
import numpy as np
from energy_storage_calculator import (
    calculate_optimal_parameters_qp,
    calculate_dispatch_schedule_qp
)


def test_optimal_parameters():
    """
    Тест функции расчета оптимальных параметров
    Аналог test_optimize_parameters() из VB
    """
    print("=" * 80)
    print("ТЕСТ 1: Расчет оптимальных параметров СНЭЭ методом QP")
    print("=" * 80)
    
    # Тестовые данные из Project_context_QP.txt (таблица, строка Баланс мощности)
    load_profile = [
        27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
        37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
    ]
    
    efficiency = 0.95  # КПД (ячейка G2 в VB)
    
    print(f"\nИсходные данные:")
    print(f"  Профиль баланса мощности (24 часа): {load_profile}")
    print(f"  КПД: {efficiency}")
    
    try:
        result = calculate_optimal_parameters_qp(load_profile, efficiency)
        
        print(f"\n✓ Расчет завершен успешно!")
        print(f"\nОПТИМАЛЬНЫЕ ПАРАМЕТРЫ:")
        print(f"  Номинальная активная входная мощность (Nin):  {result['nin']:.2f} МВт")
        print(f"  Номинальная активная выходная мощность (Nout): {result['nout']:.2f} МВт")
        print(f"  Энергия, отдаваемая в рабочем диапазоне (C):    {result['capacity']:.2f} МВтч")
        print(f"  Дефицит мощности результирующий (Dmax):        {result['deficit']:.2f} МВт")
        
        # Дополнительные расчетные параметры
        discharge_time = result['capacity'] / result['nout'] if result['nout'] > 0 else 0
        charge_energy = result['capacity'] / efficiency
        charge_time = charge_energy / result['nin'] if result['nin'] > 0 else 0
        
        print(f"\nДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ:")
        print(f"  Фактическое время разряда:                     {discharge_time:.2f} ч")
        print(f"  Энергия, затраченная на заряд:                 {charge_energy:.2f} МВтч")
        print(f"  Фактическое время заряда:                      {charge_time:.2f} ч")
        
        # Статистика по графику нагрузки СНЭЭ
        eens_load = np.array(result['eens_load'])
        charge_load = -np.sum(eens_load[eens_load < 0])
        discharge_load = np.sum(eens_load[eens_load > 0])
        
        print(f"\nСТАТИСТИКА ГРАФИКА РАБОТЫ СНЭЭ:")
        print(f"  Заряд (потребление из сети):                   {charge_load:.2f} МВтч")
        print(f"  Разряд (выдача в сеть):                        {discharge_load:.2f} МВтч")
        print(f"  Баланс заряд-разряд:                           {(discharge_load - charge_load):.4f} МВтч")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Ошибка при расчете: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_dispatch_schedule():
    """
    Тест функции расчета диспетчерского графика с заданными параметрами
    Аналог test_optimize_load() из VB
    """
    print("\n" + "=" * 80)
    print("ТЕСТ 2: Расчет диспетчерского графика СНЭЭ с заданными параметрами")
    print("=" * 80)
    
    # Тестовые данные
    load_profile = [
        27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
        37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
    ]
    
    # Параметры СНЭЭ из раздела 4.2.2 Project_context_QP.txt
    nin = 95.0      # МВт (ячейка B2 в VB)
    nout = 140.0    # МВт (ячейка B3 в VB)
    capacity = 360.0  # МВтч (400 * 0.9, ячейка B4 в VB после расчета)
    efficiency = 0.95  # КПД
    
    print(f"\nИсходные данные:")
    print(f"  Профиль баланса мощности (24 часа): {load_profile}")
    print(f"  Номинальная входная мощность (Nin):  {nin} МВт")
    print(f"  Номинальная выходная мощность (Nout): {nout} МВт")
    print(f"  Емкость в рабочем диапазоне:         {capacity} МВтч")
    print(f"  КПД:                                 {efficiency}")
    
    try:
        result = calculate_dispatch_schedule_qp(
            load_profile=load_profile,
            nin=nin,
            nout=nout,
            capacity=capacity,
            efficiency=efficiency
        )
        
        print(f"\n✓ Расчет завершен успешно!")
        print(f"\nРЕЗУЛЬТАТЫ РАСЧЕТА:")
        print(f"  Дефицит мощности результирующий (Dmax): {result['deficit']:.2f} МВт")
        print(f"  Резерв мощности результирующий (Rmax):  {result['reserve']:.2f} МВт")
        
        # Статистика
        load = np.array(load_profile)
        eens_load = np.array(result['eens_load'])
        resulting_balance = load + eens_load
        
        charge_load = -np.sum(eens_load[eens_load < 0])
        discharge_load = np.sum(eens_load[eens_load > 0])
        deficit_before = -np.sum(load[load < 0])
        deficit_after = -np.sum(resulting_balance[resulting_balance < 0])
        
        print(f"\nСТАТИСТИКА:")
        print(f"  Заряд СНЭЭ:                             {charge_load:.2f} МВтч")
        print(f"  Разряд СНЭЭ:                            {discharge_load:.2f} МВтч")
        print(f"  Дефицит энергии до СНЭЭ:                {deficit_before:.2f} МВтч")
        print(f"  Дефицит энергии после СНЭЭ:             {deficit_after:.2f} МВтч")
        print(f"  Покрыто дефицита:                       {deficit_before - deficit_after:.2f} МВтч ({(deficit_before - deficit_after) / deficit_before * 100:.1f}%)")
        
        # Вывод графика по часам (первые 8 часов для примера)
        print(f"\nГРАФИК РАБОТЫ СНЭЭ (первые 8 часов):")
        print(f"  Час | Баланс | СНЭЭ  | Результ. | SOC")
        print(f"  ----|--------|-------|----------|------")
        for i in range(8):
            print(f"  {i+1:3d} | {load[i]:6.1f} | {eens_load[i]:5.1f} | {resulting_balance[i]:8.1f} | {result['eens_energy_available'][i]:5.1f}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Ошибка при расчете: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def compare_results():
    """
    Сравнение результатов оптимизации параметров и расчета с заданными параметрами
    """
    print("\n" + "=" * 80)
    print("ТЕСТ 3: Сравнение оптимальных и заданных параметров")
    print("=" * 80)
    
    load_profile = [
        27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
        37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
    ]
    efficiency = 0.95
    
    # Получаем оптимальные параметры
    optimal = calculate_optimal_parameters_qp(load_profile, efficiency)
    
    # Заданные параметры
    given_nin = 95.0
    given_nout = 140.0
    given_capacity = 360.0
    
    print(f"\nСРАВНЕНИЕ ПАРАМЕТРОВ:")
    print(f"  Параметр                    | Оптимальные | Заданные | Разница")
    print(f"  ----------------------------|-------------|----------|--------")
    print(f"  Входная мощность (Nin), МВт | {optimal['nin']:11.2f} | {given_nin:8.2f} | {optimal['nin'] - given_nin:7.2f}")
    print(f"  Выходная мощность (Nout), МВт | {optimal['nout']:11.2f} | {given_nout:8.2f} | {optimal['nout'] - given_nout:7.2f}")
    print(f"  Емкость (C), МВтч           | {optimal['capacity']:11.2f} | {given_capacity:8.2f} | {optimal['capacity'] - given_capacity:7.2f}")
    print(f"  Дефицит (Dmax), МВт         | {optimal['deficit']:11.2f} |")
    
    # Расчет с заданными параметрами
    given_result = calculate_dispatch_schedule_qp(
        load_profile=load_profile,
        nin=given_nin,
        nout=given_nout,
        capacity=given_capacity,
        efficiency=efficiency
    )
    
    print(f"\nСРАВНЕНИЕ ДЕФИЦИТА:")
    print(f"  С оптимальными параметрами: {optimal['deficit']:.2f} МВт")
    print(f"  С заданными параметрами:    {given_result['deficit']:.2f} МВт")
    print(f"  Разница:                    {abs(optimal['deficit'] - given_result['deficit']):.2f} МВт")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ АЛГОРИТМА КВАДРАТИЧНОЙ ОПТИМИЗАЦИИ (QP)")
    print("Портировано из VB Module1.bas")
    print("=" * 80)
    
    # Запуск тестов
    result1 = test_optimal_parameters()
    result2 = test_dispatch_schedule()
    
    if result1 and result2:
        compare_results()
        
        print("\n" + "=" * 80)
        print("✓ ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✗ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("=" * 80)
        sys.exit(1)

