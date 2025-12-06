# СНЭЭ Graf - Backend API

FastAPI backend для системы визуализации диспетчерского графика СНЭЭ.

## Установка

1. Создать виртуальное окружение:
```bash
python -m venv venv
```

2. Активировать виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Документация

После запуска сервера документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Основные эндпоинты

- `GET /` - Информация об API
- `GET /api/v1/health` - Проверка работоспособности
- `GET /api/v1/default-profile` - Получить профиль по умолчанию
- `POST /api/v1/calculate` - Рассчитать диспетчерский график СНЭЭ
- `POST /api/v1/upload-excel` - Загрузить данные из Excel
- `POST /api/v1/validate-profile` - Валидация профиля баланса

## Примеры запросов

### Расчет графика
```bash
curl -X POST "http://localhost:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "load_profile": [1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261, -618, -779, -845, -927, -927, -927, -862, -799, -669, -535, -638, -370, 59, 963],
    "rated_power_mw": 500,
    "rated_capacity_mwh": 2000,
    "efficiency": 0.95
  }'
```

## Развертывание

См. инструкции в корневом README.md проекта.

