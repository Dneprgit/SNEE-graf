@echo off
chcp 65001 > nul
echo ========================================
echo СНЭЭ - Визуализация диспетчерского графика
echo ========================================
echo.

REM Проверка наличия виртуального окружения
if not exist "venv" (
    echo Виртуальное окружение не найдено!
    echo Создаю виртуальное окружение...
    python -m venv venv
    echo.
    echo Активирую окружение и устанавливаю зависимости...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    pip install PyQt6-WebEngine
    echo.
    echo Установка завершена!
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Проверка наличия .env файла
if not exist ".env" (
    echo Файл .env не найден!
    if exist "env.example" (
        echo Создаю .env из env.example...
        copy env.example .env > nul
        echo Файл .env создан. Отредактируйте его при необходимости.
        echo.
    )
)

echo Запуск приложения...
echo.
python main.py

pause

