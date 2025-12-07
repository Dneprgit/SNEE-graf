# Примеры использования API СНЭЭ Graf

Коллекция примеров для работы с REST API.

## Базовый URL

```
http://localhost:8001  # Development
https://your-domain.ru # Production
```

## 1. Health Check

Проверка работоспособности API.

### Request

```bash
curl -X GET http://localhost:8001/api/v1/health
```

### Response

```json
{
  "status": "healthy",
  "service": "SNEE Graf API"
}
```

## 2. Получение профиля по умолчанию

### Request

```bash
curl -X GET http://localhost:8001/api/v1/default-profile
```

### Response

```json
{
  "load_profile": [
    1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
    -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
    -638, -370, 59, 963
  ],
  "description": "Профиль баланса мощности из примера задания"
}
```

## 3. Расчет диспетчерского графика

Основной endpoint для расчета графика работы СНЭЭ.

### Request

```bash
curl -X POST http://localhost:8001/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "load_profile": [
      1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
      -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
      -638, -370, 59, 963
    ],
    "rated_power_mw": 500,
    "rated_capacity_mwh": 2000,
    "efficiency": 0.95
  }'
```

### Response

```json
{
  "eess_schedule": [
    -500.0, -500.0, -500.0, -500.0, -500.0, -500.0, -500.0, -500.0,
    -227.0, 261.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0,
    500.0, 500.0, 500.0, 500.0, 500.0, 370.0, -59.0, -500.0
  ],
  "resulting_balance": [
    820.0, 1015.0, 1123.0, 1269.0, 1354.0, 1291.0, 909.0, 360.0,
    0.0, 0.0, -118.0, -279.0, -345.0, -427.0, -427.0, -427.0,
    -362.0, -299.0, -169.0, -35.0, -138.0, 0.0, 0.0, 463.0
  ],
  "soc": [
    526.32, 1052.63, 1578.95, 2105.26, 2000.0, 2000.0, 2000.0, 2000.0,
    1773.0, 1511.58, 1026.32, 552.63, 78.95, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 389.47, 451.58, 978.95
  ],
  "summary": {
    "total_charge_mwh": 3486.84,
    "total_discharge_mwh": 3315.79,
    "max_charge_power_mw": 500.0,
    "max_discharge_power_mw": 500.0,
    "deficit_before_mwh": 8717.0,
    "deficit_after_mwh": 2612.0,
    "deficit_covered_mwh": 6105.0,
    "deficit_coverage_percent": 70.0,
    "surplus_before_mwh": 20449.0,
    "surplus_after_mwh": 15533.0,
    "surplus_utilized_mwh": 4916.0,
    "surplus_utilization_percent": 24.0,
    "resulting_max_deficit_mw": 427.0,
    "resulting_max_surplus_mw": 1354.0
  }
}
```

## 4. Валидация профиля

Проверка корректности входных данных.

### Request

```bash
curl -X POST http://localhost:8001/api/v1/validate-profile \
  -H "Content-Type: application/json" \
  -d '[1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261, -618, -779, -845, -927, -927, -927, -862, -799, -669, -535, -638, -370, 59, 963]'
```

### Response (успешная валидация)

```json
{
  "valid": true,
  "statistics": {
    "min": -927.0,
    "max": 1854.0,
    "mean": 496.0,
    "total_surplus": 20449.0,
    "total_deficit": 8717.0
  }
}
```

### Response (ошибка валидации)

```json
{
  "valid": false,
  "error": "Профиль должен содержать 24 значения, получено: 12"
}
```

## 5. Загрузка Excel файла

### Request

```bash
curl -X POST http://localhost:8001/api/v1/upload-excel \
  -F "file=@balance_profile.xlsx"
```

### Response (успешная загрузка)

```json
{
  "success": true,
  "load_profile": [
    1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
    -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
    -638, -370, 59, 963
  ],
  "message": "Успешно загружено 24 значений"
}
```

### Response (ошибка загрузки)

```json
{
  "detail": "Не удалось найти 24 числовых значения в файле"
}
```

## Примеры использования в разных языках

### Python (requests)

```python
import requests
import json

# Базовый URL
BASE_URL = "http://localhost:8001"

# Расчет графика
data = {
    "load_profile": [1320, 1515, 1623, ...],  # 24 значения
    "rated_power_mw": 500,
    "rated_capacity_mwh": 2000,
    "efficiency": 0.95
}

response = requests.post(
    f"{BASE_URL}/api/v1/calculate",
    json=data
)

if response.status_code == 200:
    result = response.json()
    print(f"График рассчитан успешно!")
    print(f"Покрытие дефицита: {result['summary']['deficit_coverage_percent']}%")
else:
    print(f"Ошибка: {response.json()['detail']}")

# Загрузка Excel файла
files = {'file': open('balance.xlsx', 'rb')}
response = requests.post(
    f"{BASE_URL}/api/v1/upload-excel",
    files=files
)

if response.status_code == 200:
    load_profile = response.json()['load_profile']
    print(f"Загружено {len(load_profile)} значений")
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

const BASE_URL = 'http://localhost:8001';

// Расчет графика
const calculateSchedule = async () => {
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/calculate`, {
      load_profile: [1320, 1515, 1623, ...], // 24 значения
      rated_power_mw: 500,
      rated_capacity_mwh: 2000,
      efficiency: 0.95
    });
    
    console.log('График рассчитан:', response.data);
    console.log('Покрытие дефицита:', response.data.summary.deficit_coverage_percent + '%');
  } catch (error) {
    console.error('Ошибка:', error.response?.data?.detail);
  }
};

// Загрузка Excel файла
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await axios.post(
      `${BASE_URL}/api/v1/upload-excel`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    console.log('Файл загружен:', response.data.load_profile);
  } catch (error) {
    console.error('Ошибка загрузки:', error.response?.data?.detail);
  }
};
```

### JavaScript (Fetch API)

```javascript
const BASE_URL = 'http://localhost:8001';

// Расчет графика
fetch(`${BASE_URL}/api/v1/calculate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    load_profile: [1320, 1515, 1623, ...], // 24 значения
    rated_power_mw: 500,
    rated_capacity_mwh: 2000,
    efficiency: 0.95
  })
})
  .then(response => response.json())
  .then(data => {
    console.log('Результат:', data);
  })
  .catch(error => {
    console.error('Ошибка:', error);
  });
```

### PowerShell

```powershell
$baseUrl = "http://localhost:8001"

# Расчет графика
$body = @{
    load_profile = @(1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261, -618, -779, -845, -927, -927, -927, -862, -799, -669, -535, -638, -370, 59, 963)
    rated_power_mw = 500
    rated_capacity_mwh = 2000
    efficiency = 0.95
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "$baseUrl/api/v1/calculate" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

Write-Host "Покрытие дефицита: $($response.summary.deficit_coverage_percent)%"
```

## Коды ошибок

| Код | Описание | Причина |
|-----|----------|---------|
| 200 | OK | Запрос успешно обработан |
| 400 | Bad Request | Некорректные входные данные |
| 422 | Unprocessable Entity | Ошибка валидации данных |
| 500 | Internal Server Error | Внутренняя ошибка сервера |

## Примеры ошибок

### Неверное количество значений в профиле

```json
{
  "detail": "Профиль должен содержать 24 значений"
}
```

### Неверные параметры СНЭЭ

```json
{
  "detail": "Мощность и емкость должны быть положительными"
}
```

### Неверный КПД

```json
{
  "detail": "КПД должен быть в диапазоне (0, 1]"
}
```

## Рекомендации по использованию

1. **Rate Limiting**: API не имеет ограничений в dev режиме, но в продакшене рекомендуется не более 100 запросов в минуту

2. **Размер данных**: Максимальный размер загружаемого Excel файла - 10 МБ

3. **Таймауты**: Установите таймаут не менее 30 секунд для расчетных операций

4. **Кэширование**: Кэшируйте результаты на клиенте для одинаковых входных данных

5. **Обработка ошибок**: Всегда обрабатывайте возможные ошибки API

## Полезные ссылки

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI Schema: http://localhost:8001/openapi.json

