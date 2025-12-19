# Миграция алгоритма с VB11.bas на VB12.bas

## Дата миграции
18 декабря 2025

## Обзор изменений

Файл `energy_storage_calculator_.py` был обновлен в соответствии с изменениями, внесенными в переход с VB11.bas на VB12.bas.

## Основные изменения

### 1. Функция `GetEESSOptimalLoad` (Python: `_solve_qp_optimization`)

#### 1.1 Добавлены параметризованные веса
**VB11:**
```vb
b(i) = 0.04                ' для D[]
b(im * 4 + 1) = 1         ' для Dmax
b(im * 4 + 2) = 0.0016    ' для Rmax
```

**VB12:**
```vb
dblDmaxWeight = 1
dblDWeight = dblDmaxWeight / 25
dblRmaxWeight = dblDWeight / 25

b(i) = dblDWeight
b(im * 4 + 1) = dblDmaxWeight
b(im * 4 + 2) = dblRmaxWeight
```

**Python (обновлено):**
```python
dbl_dmax_weight = 1.0
dbl_d_weight = dbl_dmax_weight / 25
dbl_rmax_weight = dbl_d_weight / 25

b[i] = dbl_d_weight
b[im * 4] = dbl_dmax_weight
b[im * 4 + 1] = dbl_rmax_weight
```

#### 1.2 Изменены границы для переменных дефицита D[]
**VB11:**
```vb
ub(i + im * 3) = MaxRealNumber
```

**VB12:**
```vb
ub(i + im * 3) = MaxDbl(0, dblSystemLoad(i))
```

**Python (обновлено):**
```python
ub[i + im * 3] = max(0.0, system_load[i])
```

#### 1.3 Улучшено начальное приближение
**VB11:**
```vb
x0(i) = lb(i) + s(i)
```

**VB12:**
```vb
x0(i) = IIf(ub(i) - s(i) >= lb(i) + s(i), lb(i) + s(i), 0.5 * lb(i) + 0.5 * ub(i))
```

**Python (обновлено):**
```python
for i in range(n):
    if ub[i] - s[i] >= lb[i] + s[i]:
        x0[i] = lb[i] + s[i]
    else:
        x0[i] = 0.5 * lb[i] + 0.5 * ub[i]
```

### 2. Функция `GetEESSOptimizedParameters` (Python: `calculate_optimal_parameters_qp`)

#### 2.1 Увеличено количество переменных и ограничений

**VB11:**
- n = im * 3 + 4 = 76 переменных: `dL[24] + CC[24] + CD[24] + Dmax + Nin + Nout + C`
- k = im * 5 = 120 ограничений: `rL[24] + rD[24] + rC[24] + rNi[24] + rNo[24]`

**VB12:**
- n = im * 4 + 4 = 100 переменных: `dL[24] + CC[24] + CD[24] + D[24] + Dmax + Nin + Nout + C`
- k = im * 6 = 144 ограничения: `rL[24] + rD[24] + rC[24] + rNi[24] + rNo[24] + rDmax[24]`

**Изменения в Python:**
```python
# VB11
n = im * 3 + 4  # 76 переменных
k = im * 5      # 120 ограничений

# VB12 (обновлено)
n = im * 4 + 4  # 100 переменных
k = im * 6      # 144 ограничения
```

#### 2.2 Добавлены параметризованные веса

**VB12:**
```vb
dblDmaxWeight = 1
dblNmaxWeight = dblDmaxWeight * 0.5 / 25
dblCapacityWeight = dblNmaxWeight / 25
dblDWeight = dblNmaxWeight / 25
```

**Python (обновлено):**
```python
dbl_dmax_weight = 1.0
dbl_nmax_weight = dbl_dmax_weight * 0.5 / 25
dbl_capacity_weight = dbl_nmax_weight / 25
dbl_d_weight = dbl_nmax_weight / 25
```

#### 2.3 Изменено ограничение rD

**VB11:**
```vb
' rD: -CC[i]/η + CD[i] + Dmax >= Load[i]
C(i + im, im * 3) = 1.0  ' Dmax
```

**VB12:**
```vb
' rD: -CC[i]/η + CD[i] + D[i] >= Load[i]
C(i + im, i + im * 3) = 1.0  ' D[i]
```

**Python (обновлено):**
```python
# Используется D[i] вместо Dmax
C[i + im][i + im * 3] = 1.0  # D[i]
```

#### 2.4 Добавлено новое ограничение rDmax

**VB12:**
```vb
' rDmax: -D[i] + Dmax >= 0
For i = 1 To im
    C(i + im * 5, i + im * 3) = -1.0  ' -D[i]
    C(i + im * 5, 1 + im * 4) = 1.0   ' Dmax
    cl(i + im * 5) = 0.0
    cu(i + im * 5) = MaxRealNumber
Next i
```

**Python (обновлено):**
```python
# Ограничение rDmax (ограничение дефицита): -D[i] + Dmax >= 0
for i in range(im):
    C[i + im * 5][i + im * 3] = -1.0  # -D[i]
    C[i + im * 5][im * 4] = 1.0  # Dmax
    cl[i + im * 5] = 0.0
    cu[i + im * 5] = max_real_number
```

#### 2.5 Изменены индексы переменных результата

**Из-за добавления D[] все индексы сдвинулись:**

**VB11:**
```vb
dblSystemWithENSSLoadDeficite = x(1 + im * 3)  ' index = 73
dblNIn = x(2 + im * 3)                          ' index = 74
dblNOut = x(3 + im * 3)                         ' index = 75
dblCapacity = x(4 + im * 3)                     ' index = 76
```

**VB12:**
```vb
dblSystemWithENSSLoadDeficite = x(1 + im * 4)  ' index = 97
dblNIn = x(2 + im * 4)                          ' index = 98
dblNOut = x(3 + im * 4)                         ' index = 99
dblCapacity = x(4 + im * 4)                     ' index = 100
```

**Python (обновлено):**
```python
dbl_system_with_enss_load_deficite = x[im * 4]      # index = 96
dbl_n_in = x[im * 4 + 1]                             # index = 97
dbl_n_out = x[im * 4 + 2]                            # index = 98
dbl_capacity = x[im * 4 + 3]                         # index = 99
```

#### 2.6 Изменены границы переменных

**VB11:**
- Все границы `ub[i] = max_real_number`

**VB12:**
```vb
' Границы для L[], CC[], CD[]
ub(i) = MaxRealNumber
ub(i + im) = MaxRealNumber
ub(i + im * 2) = MaxRealNumber

' Границы для D[]
ub(i + im * 3) = MaxDbl(0, dblSystemLoad(i))
```

**Python (обновлено):**
```python
# Границы для D[] - дефицит по часам
for i in range(im):
    lb[i + im * 3] = 0.0
    ub[i + im * 3] = max(0.0, dbl_system_load[i])
```

#### 2.7 Значительно улучшено начальное приближение

**VB12 добавил специфичное задаче начальное приближение:**

1. Расчет начальной емкости на основе суммарного баланса нагрузки
2. Расчет мощности заряда-разряда
3. Расчет дефицита мощности
4. Расчет максимального дефицита
5. Расчет входной/выходной мощности

**Python (обновлено):**
```python
# Начальное приближение емкость
dbl_max_val = 0.0
for i in range(im):
    dbl_max_val = max(lb[i] + s[i], dbl_max_val + abs(dbl_system_load[i]))

for i in range(im):
    x0[i] = dbl_max_val

x0[im * 4 + 3] = max(lb[im * 4 + 3], dbl_max_val) + s[im * 4 + 3]

# ... и так далее для остальных переменных
```

## Технические детали

### Структура переменных в VB12

**Вектор x (100 элементов):**
- `x[0..23]` - dL[] - энергия в батарее (МВтч)
- `x[24..47]` - CC[] - мощность заряда (МВт)
- `x[48..71]` - CD[] - мощность разряда (МВт)
- `x[72..95]` - D[] - дефицит мощности по часам (МВт) **[новое в VB12]**
- `x[96]` - Dmax - максимальный дефицит (МВт)
- `x[97]` - Nin - входная мощность (МВт)
- `x[98]` - Nout - выходная мощность (МВт)
- `x[99]` - C - емкость батареи (МВтч)

### Типы ограничений в VB12

1. **rL (balance)** - баланс энергии в батарее
2. **rD (power)** - баланс мощности (покрытие нагрузки)
3. **rC (capacity)** - ограничение емкости батареи
4. **rNi (input power)** - ограничение входной мощности
5. **rNo (output power)** - ограничение выходной мощности
6. **rDmax (max deficit)** - ограничение максимального дефицита **[новое в VB12]**

## Преимущества VB12

1. **Более точная модель дефицита** - добавлены почасовые переменные дефицита D[]
2. **Лучшая сходимость** - улучшенное начальное приближение
3. **Более реалистичные ограничения** - границы D[] учитывают фактическую нагрузку
4. **Параметризованные веса** - более гибкая настройка оптимизации
5. **Дополнительные ограничения** - rDmax обеспечивает консистентность решения

## Тестирование

Рекомендуется провести следующие тесты:

1. Сравнение результатов VB11 и VB12 на известных наборах данных
2. Проверка сходимости оптимизации
3. Проверка баланса заряд-разряд (должен быть ~0)
4. Проверка соблюдения всех ограничений

## Статус миграции

✅ Все изменения из VB12.bas успешно перенесены в `energy_storage_calculator_.py`

## Авторы

- Оригинальный VBA код: VB11.bas, VB12.bas
- Python миграция: energy_storage_calculator_.py





