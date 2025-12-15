# Исправление знаков в расчете результирующего баланса (QP)

## 🐛 Проблема

При расчете результирующего баланса для QP алгоритма использовалась **неправильная формула**:
```python
resulting_balance = load_profile + eess_schedule  # НЕПРАВИЛЬНО!
```

### Что происходило:
- `load_profile` = +100 МВт (дефицит)
- `eess_schedule` = +50 МВт (батарея разряжается, выдает в сеть)
- `resulting_balance` = 100 + 50 = **150 МВт** ❌

**Результат**: Дефицит УВЕЛИЧИВАЛСЯ вместо уменьшения!

## ✅ Решение

Изменена формула на **правильную**:
```python
resulting_balance = load_profile - eess_schedule  # ПРАВИЛЬНО!
```

### Теперь работает корректно:
- `load_profile` = +100 МВт (дефицит)
- `eess_schedule` = +50 МВт (батарея разряжается, покрывает дефицит)
- `resulting_balance` = 100 - 50 = **50 МВт** ✅

**Результат**: Дефицит УМЕНЬШАЕТСЯ, как и должно быть!

## 📝 Внесенные изменения

### 1. ✅ Backend API (main.py)
**Файл**: `web/backend/main.py`  
**Строка**: 336 (в эндпоинте `/api/v1/calculate-qp`)

```python
# БЫЛО:
resulting_balance = [
    request.load_profile[i] + eess_schedule[i] 
    for i in range(24)
]

# СТАЛО:
resulting_balance = [
    request.load_profile[i] - eess_schedule[i] 
    for i in range(24)
]
```

### 2. ✅ Функция get_summary_qp (energy_storage_calculator.py)
**Файл**: `web/backend/energy_storage_calculator.py`  
**Строка**: 643

```python
# БЫЛО:
resulting_balance = load + eess_schedule

# СТАЛО:
resulting_balance = load - eess_schedule
```

### 3. ✅ Тестовый скрипт (test_qp_implementation.py)
**Файл**: `web/backend/test_qp_implementation.py`  
**Строка**: 95

```python
# БЫЛО:
resulting_balance = load_profile_array + eess_load

# СТАЛО:
resulting_balance = load_profile_array - eess_load
```

### 4. ✅ Документация (QP_IMPLEMENTATION.md)
**Файл**: `web/backend/QP_IMPLEMENTATION.md`  
**Строка**: 131

Обновлена формула в разделе проверки корректности.

## 🔒 Что НЕ изменялось

### ✅ Первый вариант (НЕ QP) остался без изменений:

**main.py** (строка 117) - обычный вариант:
```python
# НЕ ТРОГАЛИ - правильная формула для первого варианта
resulting_balance = [
    request.load_profile[i] + eess_schedule[i] 
    for i in range(24)
]
```

**energy_storage_calculator.py** (строка 174) - функция get_summary:
```python
# НЕ ТРОГАЛИ - правильная формула для первого варианта
resulting_balance = load + eess_schedule
```

### Почему разные формулы?

| Вариант | Полярность баланса | Формула |
|---------|-------------------|---------|
| **Первый** | + избыток, - дефицит | `load + eess` |
| **QP** | + дефицит, - избыток | `load - eess` |

## 🎯 Логика

### Для QP (положительное = дефицит):
- Когда батарея **разряжается** (eess > 0), она **покрывает** дефицит
- Дефицит должен **уменьшаться**: `deficit - discharge = меньший_дефицит`
- Формула: `resulting_balance = load_profile - eess_schedule`

### Для первого варианта (отрицательное = дефицит):
- Когда батарея **разряжается** (eess > 0), она **добавляет** в баланс
- Баланс должен **увеличиваться**: `balance + discharge = больший_баланс`
- Формула: `resulting_balance = load_profile + eess_schedule`

## 📊 Влияние на метрики

После исправления правильно рассчитываются:
- ✅ Остаточный дефицит (deficit_after_mwh)
- ✅ Покрытый дефицит (deficit_covered_mwh)
- ✅ Остаточный избыток (surplus_after_mwh)
- ✅ Использованный избыток (surplus_utilized_mwh)
- ✅ Все проценты покрытия и использования

## 🧪 Проверка

Для проверки корректности:
```bash
cd web/backend
python test_qp_implementation.py
```

Ожидаемый результат:
- ✅ Дефицит уменьшается при разряде батареи
- ✅ Избыток уменьшается при заряде батареи
- ✅ Баланс заряд-разряд соблюдается (< 0.001)

## 📅 Дата исправления

**2024** - Исправление внесено сразу после выявления проблемы

## ✅ Статус

**Исправлено** - Все формулы для QP варианта используют правильный знак

