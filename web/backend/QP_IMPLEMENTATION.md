# Реализация QP алгоритма для СНЭЭ

## Обзор

Алгоритм квадратичной оптимизации (QP) перенесен из VB (Module1.bas, функция `GetEESSOptimalLoad`) в Python с использованием библиотеки scipy.

## Ключевые изменения

### 1. Математическая модель

**Задача оптимизации:**
- Минимизировать: F(x) = 0.5 * x' * A * x + b' * x
- При ограничениях: lb ≤ x ≤ ub и cl ≤ C' * x ≤ cu

**Структура переменных (n = 98):**
```
x[0..23]   = dL[]    - энергия в батарее по часам (МВтч)
x[24..47]  = CC[]    - мощность заряда по часам (МВт)
x[48..71]  = CD[]    - мощность разряда по часам (МВт)
x[72..95]  = D[]     - дефицит мощности по часам (МВт)
x[96]      = Dmax    - максимальный дефицит мощности (МВт)
x[97]      = Rmax    - максимальный резерв мощности (МВт)
```

### 2. Полярность баланса

**ВАЖНО:** Для QP варианта полярность баланса противоположна первому варианту:
- **Положительное значение** = дефицит (потребность в покрытии)
- **Отрицательное значение** = избыток энергии

### 3. Ограничения

**Тип 1: rL (баланс энергии, i=0..23)**
```
dL[i] - dL[i-1] - CC[i] + CD[i] = 0
```
Циклическая связь: для i=0, предыдущий элемент i-1 = 23

**Тип 2: rD (баланс мощности, i=0..23)**
```
-CC[i]/η + CD[i] + D[i] ≥ SystemLoad[i]
```

**Тип 3: rDmin (ограничение резерва, i=0..23)**
```
CC[i]/η - CD[i] + Rmax ≥ -SystemLoad[i]
```

**Тип 4: rDmax (ограничение дефицита, i=0..23)**
```
-D[i] + Dmax ≥ 0
```

## Реализация

### Файл: energy_storage_calculator.py

#### Функция `_solve_qp_optimization`
Реализует решение задачи квадратичной оптимизации методом BLEICQPSolve.

**Параметры:**
- `system_load`: баланс мощности по часам (24 значения)
- `dbl_n_in`: номинальная входная мощность (МВт)
- `dbl_n_out`: номинальная выходная мощность (МВт)
- `dbl_capacity`: емкость батареи (МВтч)

**Возвращает:**
- Вектор решения x (98 значений)

**Использует:**
- `scipy.optimize.minimize` с методом 'trust-constr'
- LinearConstraint для общих линейных ограничений
- Bounds для границ переменных

#### Функция `calculate_dispatch_schedule_qp`
Расчет диспетчерского графика СНЭЭ через QP оптимизацию.

**Возвращает словарь:**
- `eess_load`: график нагрузки СНЭЭ (24 часа)
- `soc_energy`: график заряда батареи (24 часа) в МВтч
- `deficit`: дефицит мощности (МВт)
- `reserve`: резерв мощности (МВт)

**Формула извлечения результатов:**
```python
dblEENSLoad[i] = CD[i] - CC[i]/η
```
Где CD[i] - разряд, CC[i] - заряд

### Файл: main.py

#### Эндпоинт `/api/v1/calculate-qp`
Обновлен для работы с новой структурой данных:
- Получает результаты в виде словаря из `calculate_dispatch_schedule_qp`
- Извлекает `eess_load`, `soc_energy`, `deficit`, `reserve`
- Передает SOC напрямую из QP оптимизации (dblEENSEnergyAvailable)
- Добавляет deficit и reserve в summary

### Фронтенд

#### ChartsSection_qp.jsx
Обновления:
1. Добавлены карточки для отображения deficit и reserve в "Ключевые показатели"
2. Добавлено пояснение о полярности баланса в заголовке графика
3. Обновлен экспорт в Excel для включения deficit и reserve

#### DataInputSection_qp.jsx
Добавлен информационный блок о полярности баланса в разделе редактирования.

## Проверка корректности

### 1. Баланс заряд-разряд
```python
balance = sum(CC[i] - CD[i]) for i in range(24)
assert abs(balance) < 0.001  # Должно быть ~0
```

### 2. Ограничения SOC
```python
assert all(0 <= dL[i] <= dblCapacity for i in range(24))
```

### 3. Ограничения мощности
```python
assert all(0 <= CC[i] <= dblNIn * η for i in range(24))
assert all(0 <= CD[i] <= dblNOut for i in range(24))
```

### 4. Результирующий баланс
```python
resulting_balance = load_profile - eess_load
# Для QP: вычитаем, так как разряд (положительный) покрывает дефицит (положительный)
# Проверяем, что deficit и surplus корректно отражены
```

## Тестирование

Создан файл `test_qp_implementation.py` для автоматической проверки:
- Баланс заряд-разряд
- Ограничения SOC
- Ограничения мощности
- Корректность deficit и reserve
- Итоговая статистика

## Критические моменты

1. **Индексация**: VB использует индексацию с 1, Python с 0 - требуется корректная трансформация
2. **Полярность**: QP вариант имеет противоположную полярность баланса
3. **Циклический индекс**: для i=0, предыдущий элемент i-1 = 23
4. **Масштаб чисел**: MaxRealNumber = 1e300 в VB заменен на np.inf в scipy
5. **Коды завершения**: успешные коды (1,2,4,5,7,8), остальные - ошибки

## Зависимости

Требуемые библиотеки:
```
scipy>=1.9.0
numpy>=1.23.0
```

Установка:
```bash
pip install scipy numpy
```

## Пример использования

```python
from energy_storage_calculator_ import EnergyStorageCalculator_qp

# Создание калькулятора
calculator = EnergyStorageCalculator_qp(
    rated_power_mw=54.0,
    rated_capacity_mwh=535.0,
    efficiency=0.95
)

# Профиль баланса (для QP: + дефицит, - избыток)
load_profile = [27, 38, 84, ...]  # 24 значения

# Расчет
result = calculator.calculate_dispatch_schedule_qp(load_profile)

# Результаты
eess_load = result['eess_load']  # График нагрузки СНЭЭ
soc_energy = result['soc_energy']  # График заряда батареи
deficit = result['deficit']  # Дефицит мощности
reserve = result['reserve']  # Резерв мощности
```

## Соответствие VB коду

| VB (Module1.bas) | Python (energy_storage_calculator.py) |
|------------------|----------------------------------------|
| GetEESSOptimalLoad | calculate_dispatch_schedule_qp |
| BLEICQPSolve | scipy.optimize.minimize (trust-constr) |
| dblEENSEnergyAvailable | soc_energy (x[0:24]) |
| dblEENSLoad | eess_load (CD - CC/η) |
| dblSystemWithENSSLoadDeficite | deficit (x[96]) |
| dblSystemWithENSSLoadReserve | reserve (x[97]) |

## Статус

✅ QP оптимизация реализована
✅ API обновлен
✅ Фронтенд обновлен
✅ Документация создана
✅ Тесты подготовлены

## Автор

Реализация выполнена на основе алгоритма из VB (Module1.bas) с использованием scipy.optimize вместо alglib DLL.

