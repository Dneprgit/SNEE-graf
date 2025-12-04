# Инструкция по установке и запуску

## Быстрый старт (Windows)

### Вариант 1: Запуск через BAT файл (рекомендуется)

1. Убедитесь, что установлен Python 3.8 или выше
2. Дважды щелкните по файлу `run.bat`
3. Скрипт автоматически:
   - Создаст виртуальное окружение (если его нет)
   - Установит все зависимости
   - Создаст файл .env (если его нет)
   - Запустит приложение

### Вариант 2: Ручная установка

1. Откройте командную строку в папке проекта

2. Создайте виртуальное окружение:
```bash
python -m venv venv
```

3. Активируйте окружение:
```bash
venv\Scripts\activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Создайте файл .env:
```bash
copy env.example .env
```

6. Запустите приложение:
```bash
python main.py
```

## Тестирование

Для проверки корректности алгоритма расчета:

```bash
python test_calculator.py
```

Для создания примера Excel файла:

```bash
python example_data.py
```

## Компиляция в EXE

### Через BAT файл:

Дважды щелкните по файлу `build.bat`

### Вручную:

```bash
venv\Scripts\activate
pyinstaller --clean ^
            --name="SNEE_Graf" ^
            --windowed ^
            --onefile ^
            --add-data="env.example;." ^
            --hidden-import="PyQt6.QtWebEngineWidgets" ^
            --hidden-import="plotly" ^
            --hidden-import="openpyxl" ^
            main.py
```

Результат будет в папке `dist\SNEE_Graf.exe`

## Использование EXE файла

1. Скопируйте `SNEE_Graf.exe` в любую папку
2. Создайте в той же папке файл `.env` (можно скопировать из `env.example`)
3. Запустите `SNEE_Graf.exe`

**Важно:** Файл `.env` должен находиться в той же папке, что и EXE файл!

## Решение проблем

### Ошибка: "Python не найден"

Установите Python с официального сайта: https://www.python.org/downloads/

При установке обязательно отметьте галочку "Add Python to PATH"

### Ошибка при установке зависимостей

Обновите pip:
```bash
python -m pip install --upgrade pip
```

Затем повторите установку:
```bash
pip install -r requirements.txt
```

### Ошибка: "ModuleNotFoundError"

Убедитесь, что виртуальное окружение активировано:
```bash
venv\Scripts\activate
```

### Приложение не запускается

1. Проверьте, что установлены все зависимости из `requirements.txt`
2. Проверьте, что файл `.env` существует
3. Запустите тестовый скрипт для диагностики:
```bash
python test_calculator.py
```

### График не отображается

Это может быть связано с QtWebEngine. Попробуйте:
```bash
pip install --upgrade PyQt6 PyQt6-WebEngine
```

## Системные требования

- **ОС:** Windows 10/11 (64-bit)
- **Python:** 3.8 или выше
- **RAM:** Минимум 2 GB
- **Место на диске:** ~500 MB (включая Python и зависимости)

## Структура файлов после установки

```
SNEE_graf/
├── venv/                    # Виртуальное окружение (создается автоматически)
├── main.py                  # Главный файл приложения
├── main_window.py          # GUI
├── energy_storage_calculator.py  # Алгоритм расчета
├── data_manager.py         # Работа с данными
├── visualization.py        # Графики
├── requirements.txt        # Зависимости
├── .env                    # Конфигурация (создается автоматически)
├── env.example             # Пример конфигурации
├── run.bat                 # Скрипт запуска
├── build.bat               # Скрипт компиляции
├── test_calculator.py      # Тесты
├── example_data.py         # Создание примера
├── README.md               # Документация
├── INSTALL.md              # Эта инструкция
└── dist/                   # Скомпилированный EXE (после build.bat)
    └── SNEE_Graf.exe
```

## Обновление программы

Если вы получили обновленную версию:

1. Сохраните ваш файл `.env` (если изменяли настройки)
2. Замените файлы программы новыми версиями
3. Обновите зависимости:
```bash
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

## Поддержка

При возникновении проблем:

1. Проверьте, что следуете инструкциям точно
2. Прочитайте раздел "Решение проблем" выше
3. Запустите тестовый скрипт `test_calculator.py` для диагностики
4. Обратитесь к разработчику с описанием проблемы и текстом ошибки

