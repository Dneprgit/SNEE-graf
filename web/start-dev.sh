#!/bin/bash

# Скрипт для одновременного запуска backend и frontend на Linux/Mac

echo "========================================"
echo "Starting SNEE Graf Development Environment"
echo "========================================"
echo ""

# Проверка наличия tmux
if ! command -v tmux &> /dev/null; then
    echo "tmux not found. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y tmux
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install tmux
    fi
fi

# Создание tmux сессии
SESSION_NAME="snee-graf"

# Проверка существующей сессии
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? == 0 ]; then
    echo "Session $SESSION_NAME already exists. Attaching..."
    tmux attach-session -t $SESSION_NAME
    exit 0
fi

# Создание новой сессии
tmux new-session -d -s $SESSION_NAME

# Окно 1: Backend
tmux rename-window -t $SESSION_NAME:0 'Backend'
tmux send-keys -t $SESSION_NAME:0 'cd backend' C-m
tmux send-keys -t $SESSION_NAME:0 'source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate' C-m
tmux send-keys -t $SESSION_NAME:0 'pip install -r requirements.txt' C-m
tmux send-keys -t $SESSION_NAME:0 'uvicorn main:app --reload --host 0.0.0.0 --port 8000' C-m

# Окно 2: Frontend
tmux new-window -t $SESSION_NAME:1 -n 'Frontend'
tmux send-keys -t $SESSION_NAME:1 'cd frontend' C-m
tmux send-keys -t $SESSION_NAME:1 'npm install' C-m
tmux send-keys -t $SESSION_NAME:1 'npm run dev' C-m

# Окно 3: Команды
tmux new-window -t $SESSION_NAME:2 -n 'Commands'
tmux send-keys -t $SESSION_NAME:2 'echo "SNEE Graf Development Environment"' C-m
tmux send-keys -t $SESSION_NAME:2 'echo "Backend:  http://localhost:8000"' C-m
tmux send-keys -t $SESSION_NAME:2 'echo "Frontend: http://localhost:3000"' C-m
tmux send-keys -t $SESSION_NAME:2 'echo "API Docs: http://localhost:8000/docs"' C-m
tmux send-keys -t $SESSION_NAME:2 'echo ""' C-m
tmux send-keys -t $SESSION_NAME:2 'echo "Use Ctrl+B then number to switch windows"' C-m
tmux send-keys -t $SESSION_NAME:2 'echo "Use Ctrl+B then D to detach"' C-m

# Выбор первого окна
tmux select-window -t $SESSION_NAME:0

# Подключение к сессии
tmux attach-session -t $SESSION_NAME

