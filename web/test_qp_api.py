"""
Тестирование QP API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8002"

def test_optimal_parameters_qp():
    """Тест расчета оптимальных параметров QP"""
    print("=" * 60)
    print("ТЕСТ: Расчет оптимальных параметров QP")
    print("=" * 60)
    
    # Тестовые данные из Project_context_QP.txt
    load_profile = [
        27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
        37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
    ]
    
    data = {
        "load_profile": load_profile,
        "efficiency": 0.95
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/calculate-optimal-parameters-qp",
            json=data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Запрос успешен")
            print(f"\nОптимальные параметры:")
            print(f"  Nin (входная мощность):  {result['nin']:.2f} МВт")
            print(f"  Nout (выходная мощность): {result['nout']:.2f} МВт")
            print(f"  Capacity (емкость):       {result['capacity']:.2f} МВтч")
            print(f"  Deficit (дефицит):        {result['deficit']:.2f} МВт")
            print(f"\n  Сообщение: {result.get('message', '')}")
            
            # Дополнительные параметры
            discharge_time = result['capacity'] / result['nout'] if result['nout'] > 0 else 0
            charge_energy = result['capacity'] / 0.95
            charge_time = charge_energy / result['nin'] if result['nin'] > 0 else 0
            
            print(f"\nДополнительные параметры:")
            print(f"  Время разряда:            {discharge_time:.2f} ч")
            print(f"  Энергия заряда:           {charge_energy:.2f} МВтч")
            print(f"  Время заряда:             {charge_time:.2f} ч")
            
            return True
        else:
            print(f"\n✗ Ошибка: {response.status_code}")
            print(f"  {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Исключение: {str(e)}")
        return False


def test_dispatch_schedule_qp():
    """Тест расчета диспетчерского графика QP с заданными параметрами"""
    print("\n" + "=" * 60)
    print("ТЕСТ: Расчет диспетчерского графика QP")
    print("=" * 60)
    
    load_profile = [
        27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
        37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
    ]
    
    data = {
        "load_profile": load_profile,
        "nin": 95.0,
        "nout": 140.0,
        "capacity": 360.0,
        "efficiency": 0.95
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/calculate-dispatch-qp",
            json=data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Запрос успешен")
            print(f"\nРезультаты:")
            print(f"  Deficit (дефицит):  {result['deficit']:.2f} МВт")
            print(f"  Reserve (резерв):   {result['reserve']:.2f} МВт")
            print(f"\n  Сообщение: {result.get('message', '')}")
            
            # Показываем первые 8 часов графика
            print(f"\nГрафик работы (первые 8 часов):")
            print(f"  Час | Баланс | СНЭЭ | Результ. | SOC")
            print(f"  ----|--------|------|----------|-----")
            for i in range(8):
                print(f"  {i+1:3d} | {load_profile[i]:6.1f} | {result['eens_schedule'][i]:4.1f} | {result['resulting_balance'][i]:8.1f} | {result['soc'][i]:4.1f}")
            
            return True
        else:
            print(f"\n✗ Ошибка: {response.status_code}")
            print(f"  {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Исключение: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ QP API ENDPOINTS")
    print("=" * 60 + "\n")
    
    test1 = test_optimal_parameters_qp()
    test2 = test_dispatch_schedule_qp()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    else:
        print("✗ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    print("=" * 60 + "\n")

