"""
Тестовый скрипт для проверки API эндпоинтов PPW варианта
"""
import requests
import json

API_BASE = "http://localhost:8002/api/v1"

def test_health():
    """Проверка health endpoint"""
    print("\n" + "="*60)
    print("ТЕСТ: Health Check")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_calculate_load():
    """Тест расчета нагрузки СНЭЭ"""
    print("\n" + "="*60)
    print("ТЕСТ: Calculate Load")
    print("="*60)
    
    # Тестовые данные: профиль баланса с дефицитом и избытком
    load_profile = [50, 40, 30, 20, -10, -20, -30, -40, -30, -20, -10, 0,
                    10, 20, 30, 40, 50, 60, 40, 20, 10, 0, -10, -20]
    
    # Параметры СНЭЭ согласно API схеме
    payload = {
        "system_load": load_profile,
        "rated_power_in_mw": 95.0,      # Входная мощность
        "rated_power_out_mw": 140.0,    # Выходная мощность
        "capacity_mwh": 360.0,          # Емкость
        "efficiency": 0.95              # КПД
    }
    
    print(f"Отправка запроса...")
    print(f"Профиль: {len(load_profile)} значений")
    print(f"Параметры: rated_power_in={payload['rated_power_in_mw']} МВт, rated_power_out={payload['rated_power_out_mw']} МВт, capacity={payload['capacity_mwh']} МВтч")
    
    response = requests.post(
        f"{API_BASE}/ppw/calculate-load",
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Запрос успешен")
        print(f"\nРезультаты:")
        print(f"  eess_load: {len(result.get('eess_load', []))} значений")
        print(f"  resulting_balance: {len(result.get('resulting_balance', []))} значений")
        print(f"  soc: {len(result.get('soc', []))} значений")
        print(f"  termination_code: {result.get('termination_code')}")
        
        # Вывод первых значений
        if 'eess_load' in result and len(result['eess_load']) > 0:
            print(f"\n  Первые 5 значений eess_load: {result['eess_load'][:5]}")
        if 'resulting_balance' in result and len(result['resulting_balance']) > 0:
            print(f"  Первые 5 значений resulting_balance: {result['resulting_balance'][:5]}")
        if 'soc' in result and len(result['soc']) > 0:
            print(f"  Первые 5 значений SOC: {result['soc'][:5]}")
            
        assert 'eess_load' in result
        assert 'resulting_balance' in result
        assert 'soc' in result
        print("\n✓ Calculate Load test passed")
    else:
        print(f"✗ Ошибка: {response.text}")
        raise AssertionError("API request failed")


def test_calculate_optimal_parameters():
    """Тест расчета оптимальных параметров"""
    print("\n" + "="*60)
    print("ТЕСТ: Calculate Optimal Parameters")
    print("="*60)
    
    # Тестовые данные
    load_profile = [50, 40, 30, 20, -10, -20, -30, -40, -30, -20, -10, 0,
                    10, 20, 30, 40, 50, 60, 40, 20, 10, 0, -10, -20]
    
    efficiency = 0.95
    
    payload = {
        "system_load": load_profile,
        "efficiency": efficiency
    }
    
    print(f"Отправка запроса...")
    print(f"Профиль: {len(load_profile)} значений")
    print(f"КПД: {efficiency}")
    
    response = requests.post(
        f"{API_BASE}/ppw/calculate-optimal-parameters",
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Запрос успешен")
        print(f"\nОптимальные параметры:")
        print(f"  rated_power_in_mw: {result.get('rated_power_in_mw', 'N/A'):.2f} МВт")
        print(f"  rated_power_out_mw: {result.get('rated_power_out_mw', 'N/A'):.2f} МВт")
        print(f"  capacity_mwh: {result.get('capacity_mwh', 'N/A'):.2f} МВт*ч")
        print(f"  termination_code: {result.get('termination_code')}")
        
        # Дополнительная информация
        if 'summary' in result:
            summary = result['summary']
            print(f"\n  Сводка:")
            for key, value in summary.items():
                if isinstance(value, (int, float)):
                    print(f"    {key}: {value:.2f}")
                else:
                    print(f"    {key}: {value}")
            
        assert 'rated_power_in_mw' in result
        assert 'rated_power_out_mw' in result
        assert 'capacity_mwh' in result
        print("\n✓ Calculate Optimal Parameters test passed")
    else:
        print(f"✗ Ошибка: {response.text}")
        raise AssertionError("API request failed")


def test_realistic_scenario():
    """Тест с реалистичным сценарием из промпта"""
    print("\n" + "="*60)
    print("ТЕСТ: Realistic Scenario (из промпта)")
    print("="*60)
    
    # Данные из промпта
    load_profile = [52, 50, 49, 50, 54, 62, 89, 127, 135, 139, 136, 129,
                    117, 111, 107, 105, 101, 99, 106, 119, 122, 103, 75, 61]
    
    efficiency = 0.95
    
    payload = {
        "system_load": load_profile,
        "efficiency": efficiency
    }
    
    print(f"Отправка запроса с данными из промпта...")
    print(f"Min: {min(load_profile)}, Max: {max(load_profile)}, Avg: {sum(load_profile)/len(load_profile):.2f}")
    
    response = requests.post(
        f"{API_BASE}/ppw/calculate-optimal-parameters",
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Запрос успешен")
        print(f"\nОптимальные параметры для реалистичного профиля:")
        print(f"  Входная мощность: {result.get('rated_power_in_mw', 'N/A'):.2f} МВт")
        print(f"  Выходная мощность: {result.get('rated_power_out_mw', 'N/A'):.2f} МВт")
        print(f"  Емкость: {result.get('capacity_mwh', 'N/A'):.2f} МВт*ч")
        print(f"  Код завершения: {result.get('termination_code')}")
        
        if 'summary' in result:
            summary = result['summary']
            print(f"\n  Сводная информация:")
            for key, value in summary.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.2f}")
                else:
                    print(f"    {key}: {value}")
        
        print("\n✓ Realistic Scenario test passed")
    else:
        print(f"✗ Ошибка: {response.text}")
        raise AssertionError("API request failed")


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  ТЕСТИРОВАНИЕ PPW API ENDPOINTS                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    try:
        test_health()
        test_calculate_load()
        test_calculate_optimal_parameters()
        test_realistic_scenario()
        
        print("\n" + "="*60)
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n✗ ТЕСТ ПРОВАЛЕН: {e}\n")
        raise

