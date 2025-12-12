@echo off
REM Запуск FastAPI сервера для СНЭЭ Graf

echo Starting SNEE Graf API Server...
echo.

REM Проверка наличия виртуального окружения
if exist venv (
    call venv\Scripts\activate
) else (
    echo Warning: Virtual environment not found. Using global Python.
)

REM Запуск сервера
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002

pause

