@echo off
chcp 65001 > nul
echo ========================================
echo Компиляция СНЭЭ в EXE файл
echo ========================================
echo.

REM Активация виртуального окружения
if not exist "venv" (
    echo ОШИБКА: Виртуальное окружение не найдено!
    echo Сначала запустите run.bat для установки зависимостей.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Компиляция приложения...
echo.

pyinstaller --clean ^
            --name="SNEE_Graf" ^
            --windowed ^
            --onefile ^
            --add-data="env.example;." ^
            --hidden-import="PyQt6.QtWebEngineWidgets" ^
            --hidden-import="plotly" ^
            --hidden-import="openpyxl" ^
            main.py

echo.
if exist "dist\SNEE_Graf.exe" (
    echo ========================================
    echo Компиляция успешно завершена!
    echo.
    echo Исполняемый файл: dist\SNEE_Graf.exe
    echo ========================================
    echo.
    echo ВАЖНО: При первом запуске EXE файла создайте
    echo файл .env рядом с программой (пример в env.example^)
    echo.
) else (
    echo ОШИБКА: Не удалось создать исполняемый файл
)

pause

