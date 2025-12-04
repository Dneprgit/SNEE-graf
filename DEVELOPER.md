# Руководство разработчика

## Быстрый старт для разработки

### Настройка окружения

```bash
# 1. Клонировать репозиторий
cd "C:\den\Cursor\SNEE graf"

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать окружение
venv\Scripts\activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Создать .env файл
copy env.example .env

# 6. Запустить тесты
python test_calculator.py

# 7. Запустить приложение
python main.py
```

### IDE настройки

#### VS Code / Cursor
Рекомендуемые расширения:
- Python (Microsoft)
- Pylance (Microsoft)
- Python Test Explorer

Настройки (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm
1. File → Settings → Project → Python Interpreter
2. Выбрать `venv/Scripts/python.exe`
3. Enable "Auto-reload on external changes"

## Архитектура приложения

### Модульная структура

```
┌─────────────────┐
│    main.py      │  Точка входа
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       main_window.py                │  GUI Controller
│  ┌───────────────────────────────┐  │
│  │ - Управление состоянием       │  │
│  │ - Обработка событий           │  │
│  │ - Координация модулей         │  │
│  └───────────────────────────────┘  │
└─┬───────────┬──────────────┬────────┘
  │           │              │
  ▼           ▼              ▼
┌──────────┐ ┌─────────────┐ ┌──────────────┐
│ Calculator│ │   Data      │ │Visualization │
│           │ │  Manager    │ │              │
│ - Алгоритм│ │ - Import    │ │ - Plotly     │
│ - Расчеты │ │ - Export    │ │ - Графики    │
└──────────┘ └─────────────┘ └──────────────┘
     │              │                │
     ▼              ▼                ▼
  NumPy         Pandas            Plotly
```

### Потоки данных

```
Пользовательский ввод
    │
    ▼
MainWindow.on_table_changed() / on_parameters_changed()
    │
    ▼
MainWindow.calculate_and_update()
    │
    ├─► EnergyStorageCalculator.calculate_dispatch_schedule()
    │       │
    │       ├─► Расчет лимитов
    │       ├─► Water-filling
    │       └─► Формирование графика
    │
    ├─► EnergyStorageCalculator.get_summary()
    │       │
    │       └─► Статистика
    │
    └─► ChartGenerator.create_dispatch_chart()
            │
            └─► Plotly Figure
                    │
                    ▼
            QWebEngineView.setHtml()
```

## Ключевые компоненты

### 1. EnergyStorageCalculator

**Назначение:** Расчет оптимального диспетчерского графика

**Основные методы:**
```python
def __init__(self, rated_power_mw, rated_capacity_mwh, efficiency):
    """Инициализация с параметрами СНЭЭ"""

def calculate_dispatch_schedule(self, load_profile):
    """Главный метод расчета, возвращает np.ndarray[24]"""

def get_summary(self, load_profile, eess_schedule):
    """Расчет сводной статистики, возвращает dict"""

def _get_level_bounded(self, lb, ub, dir_factor, area):
    """Water-filling алгоритм (приватный метод)"""
```

**Алгоритм:**
1. Расчет почасовых лимитов с учетом КПД полуцикла
2. Определение используемой энергии (min из возможностей)
3. Water-filling для уровня заряда
4. Water-filling для уровня разряда
5. Формирование графика мощности на шинах

**Сложность:** O(n log n) где n = 24 (из-за сортировки в water-filling)

### 2. MainWindow (PyQt6)

**Назначение:** Управление GUI и состоянием приложения

**Ключевые виджеты:**
```python
self.input_table: QTableWidget      # Исходные данные (2×24)
self.results_table: QTableWidget    # Результаты (3×24)
self.summary_text: QTextEdit        # Сводка
self.web_view: QWebEngineView       # График

self.power_input: QLineEdit         # Мощность
self.capacity_input: QLineEdit      # Емкость
self.efficiency_input: QLineEdit    # КПД
```

**Важные методы:**
```python
def calculate_and_update(self):
    """Пересчет и обновление всех элементов"""

def _update_chart(self):
    """Обновление Plotly графика в QWebEngineView"""

def import_from_excel(self):
    """Диалог импорта и обработка"""

def export_to_excel(self):
    """Диалог экспорта и сохранение"""
```

**Особенности:**
- Использование QTimer для задержки пересчета (500 мс)
- Блокировка сигналов при программном изменении таблиц
- Валидаторы для полей ввода (QDoubleValidator)

### 3. ChartGenerator (Plotly)

**Назначение:** Генерация интерактивных графиков

**Структура графика:**
```python
fig = make_subplots(rows=2, cols=1)
# Row 1: Баланс мощности + график СНЭЭ
# Row 2: Состояние заряда батареи (SOC)
```

**Серии данных:**
1. Исходный баланс (fill area, розовый)
2. Заряд СНЭЭ (bar, синий)
3. Разряд СНЭЭ (bar, зеленый)
4. Результирующий баланс (line, черный)
5. SOC батареи (line+fill, фиолетовый)

**Интерактивность:**
- hover tooltips
- zoom/pan
- series toggle
- export to PNG

### 4. DataManager

**Назначение:** Импорт/экспорт данных

**Методы:**
```python
@staticmethod
def import_from_excel(file_path):
    """Умный поиск 24 значений в Excel файле"""

@staticmethod
def export_to_excel(file_path, load_profile, eess_schedule, summary):
    """Экспорт с двумя листами и форматированием"""

@staticmethod
def get_default_profile():
    """Профиль из задания"""
```

## Разработка новых функций

### Добавление нового параметра СНЭЭ

1. **Добавить в env.example и .env:**
```bash
DEFAULT_NEW_PARAMETER=123
```

2. **Добавить в MainWindow.__init__():**
```python
self.default_new_param = float(os.getenv('DEFAULT_NEW_PARAMETER', '123'))
```

3. **Добавить виджет в _create_parameters_group():**
```python
self.new_param_input = QLineEdit(str(self.default_new_param))
self.new_param_input.setValidator(validator)
self.new_param_input.textChanged.connect(self.on_parameters_changed)
```

4. **Добавить getter:**
```python
def get_new_param(self) -> float:
    try:
        return float(self.new_param_input.text())
    except:
        return self.default_new_param
```

5. **Использовать в расчетах:**
```python
new_param = self.get_new_param()
calculator = EnergyStorageCalculator(..., new_param)
```

### Добавление нового типа графика

1. **Добавить метод в ChartGenerator:**
```python
@staticmethod
def create_new_chart_type(data, params):
    fig = go.Figure()
    # ... создание графика
    return fig
```

2. **Добавить в MainWindow:**
```python
def _update_new_chart(self):
    fig = ChartGenerator.create_new_chart_type(self.data, self.params)
    # Отобразить в новом QWebEngineView или заменить существующий
```

3. **Добавить кнопку:**
```python
new_chart_btn = QPushButton("Новый график")
new_chart_btn.clicked.connect(self._update_new_chart)
```

### Добавление нового формата экспорта

1. **Добавить метод в DataManager:**
```python
@staticmethod
def export_to_new_format(file_path, data):
    try:
        # ... логика экспорта
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False
```

2. **Добавить кнопку в MainWindow:**
```python
export_new_btn = QPushButton("Экспорт в новый формат")
export_new_btn.clicked.connect(self.export_to_new_format)

def export_to_new_format(self):
    file_path, _ = QFileDialog.getSaveFileName(...)
    if file_path:
        success = DataManager.export_to_new_format(file_path, self.data)
        # ... обработка результата
```

## Тестирование

### Модульные тесты

Создайте `test_module_name.py`:
```python
import unittest
from module_name import ClassName

class TestClassName(unittest.TestCase):
    
    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.obj = ClassName(params)
    
    def test_feature_name(self):
        """Тест конкретной функции"""
        result = self.obj.method(input_data)
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        """Тест граничного случая"""
        with self.assertRaises(ValueError):
            self.obj.method(invalid_input)

if __name__ == '__main__':
    unittest.main()
```

### Интеграционные тесты

```python
def test_full_workflow():
    """Тест полного рабочего процесса"""
    # 1. Загрузка данных
    profile = DataManager.get_default_profile()
    
    # 2. Расчет
    calc = EnergyStorageCalculator(500, 2000, 0.95)
    schedule = calc.calculate_dispatch_schedule(profile)
    
    # 3. Статистика
    summary = calc.get_summary(profile, schedule)
    
    # 4. Визуализация
    fig = ChartGenerator.create_dispatch_chart(profile, schedule, 500, 2000, 0.95)
    
    # 5. Проверки
    assert len(schedule) == 24
    assert abs(np.sum(schedule)) < 0.1
    assert summary['deficit_coverage_percent'] > 0
```

### GUI тестирование

Используйте pytest-qt:
```python
def test_main_window(qtbot):
    """Тест главного окна"""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Проверка начального состояния
    assert window.power_input.text() == "500"
    
    # Симуляция ввода
    window.power_input.setText("1000")
    qtbot.wait(600)  # Ждем пересчета
    
    # Проверка результата
    assert window.eess_schedule is not None
```

## Отладка

### Логирование

Добавьте логирование:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('snee.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Использование
logger.debug(f"Расчет с параметрами: power={power}, capacity={capacity}")
logger.info("Расчет завершен успешно")
logger.error(f"Ошибка расчета: {e}")
```

### Профилирование

```python
import cProfile
import pstats

# Профилирование функции
profiler = cProfile.Profile()
profiler.enable()

calculator.calculate_dispatch_schedule(profile)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Топ 10 функций
```

### Дебаггер

```python
# Точка останова
import pdb; pdb.set_trace()

# Или в VS Code/Cursor: F9 для breakpoint
```

## Оптимизация

### Производительность

1. **NumPy векторизация:**
```python
# Плохо (цикл)
result = []
for i in range(len(arr)):
    result.append(arr[i] * 2)

# Хорошо (векторизация)
result = arr * 2
```

2. **Кэширование:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    # ... долгие расчеты
    return result
```

3. **Ленивые вычисления:**
```python
# Пересчет только при изменении
if self._cache_dirty:
    self._cached_result = self._calculate()
    self._cache_dirty = False
return self._cached_result
```

### Память

1. **Использование генераторов:**
```python
# Плохо (весь список в памяти)
data = [process(x) for x in huge_list]

# Хорошо (генератор)
data = (process(x) for x in huge_list)
```

2. **Очистка больших объектов:**
```python
del large_dataframe
import gc
gc.collect()
```

## Стиль кода

### PEP 8

Проверка:
```bash
pip install pylint
pylint *.py
```

Автоформатирование:
```bash
pip install black
black *.py
```

### Документация

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Краткое описание функции.
    
    Подробное описание работы функции, алгоритмов,
    особенностей использования.
    
    Args:
        param1: Описание первого параметра
        param2: Описание второго параметра
    
    Returns:
        Описание возвращаемого значения
    
    Raises:
        ValueError: Когда и почему
        TypeError: Когда и почему
    
    Example:
        >>> function_name(value1, value2)
        result
    """
    pass
```

## Релиз новой версии

### Чеклист

1. **Код:**
   - [ ] Все тесты проходят
   - [ ] Нет linter ошибок
   - [ ] Производительность приемлема
   - [ ] Нет memory leaks

2. **Документация:**
   - [ ] README.md обновлен
   - [ ] VERSION.md с описанием изменений
   - [ ] Комментарии в коде актуальны
   - [ ] Примеры работают

3. **Тестирование:**
   - [ ] Ручное тестирование всех функций
   - [ ] Тестирование на чистой системе
   - [ ] EXE файл работает
   - [ ] Импорт/экспорт работает

4. **Релиз:**
   - [ ] Обновить VERSION.md
   - [ ] Создать git tag
   - [ ] Скомпилировать EXE
   - [ ] Создать архив с документацией
   - [ ] Опубликовать release notes

### Версионирование (Semantic Versioning)

```
MAJOR.MINOR.PATCH

MAJOR - несовместимые изменения API
MINOR - новая функциональность (обратно совместимая)
PATCH - исправления ошибок
```

Примеры:
- `1.0.0` → `1.0.1` - исправлена ошибка
- `1.0.1` → `1.1.0` - добавлен экспорт в CSV
- `1.1.0` → `2.0.0` - изменен формат .env файла

## Полезные ссылки

### Документация
- [Python](https://docs.python.org/3/)
- [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [NumPy](https://numpy.org/doc/stable/)
- [Plotly](https://plotly.com/python/)

### Инструменты
- [PyInstaller](https://pyinstaller.org/)
- [Black](https://black.readthedocs.io/)
- [Pylint](https://pylint.org/)

### Сообщество
- [Stack Overflow - PyQt](https://stackoverflow.com/questions/tagged/pyqt)
- [Stack Overflow - Plotly](https://stackoverflow.com/questions/tagged/plotly)
- [GitHub - Energy Storage](https://github.com/topics/energy-storage)

---

**Удачной разработки! 🚀**

