@echo off
cd backend
if not exist venv python -m venv venv
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002