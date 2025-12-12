@echo off
REM Скрипт для одновременного запуска backend и frontend на Windows

echo ========================================
echo Starting SNEE Graf Development Environment
echo ========================================
echo.

REM Запуск backend в новом окне
echo Starting Backend (FastAPI)...
start "SNEE Backend" cmd /k "cd backend && if exist venv\Scripts\activate (venv\Scripts\activate) && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002"

REM Небольшая задержка
timeout /t 3 /nobreak >nul

REM Запуск frontend в новом окне
echo Starting Frontend (React + Vite)...
start "SNEE Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Development servers are starting...
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3002
echo API Docs: http://localhost:8002/docs
echo ========================================
echo.
echo Press any key to close this window (servers will continue running)
pause >nul

