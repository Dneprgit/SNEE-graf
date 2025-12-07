#!/bin/bash

# Скрипт перезапуска SNЭЭ Graf
# Использование: ./restart.sh [backend|frontend|all]

show_usage() {
    echo "Использование: $0 [backend|frontend|all]"
    echo ""
    echo "Опции:"
    echo "  backend   - Перезапустить только backend"
    echo "  frontend  - Перезапустить только frontend"
    echo "  all       - Перезапустить все контейнеры (по умолчанию)"
    exit 1
}

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Переходим в директорию проекта
cd /opt/snee-graf || { echo "Ошибка: Директория /opt/snee-graf не найдена"; exit 1; }

SERVICE=${1:-all}

case $SERVICE in
    backend)
        echo -e "${YELLOW}Перезапуск Backend...${NC}"
        docker-compose restart snee-backend
        echo -e "${GREEN}✓ Backend перезапущен${NC}"
        sleep 5
        echo "Проверка:"
        curl -s http://localhost:8001/api/v1/health | jq
        ;;
    
    frontend)
        echo -e "${YELLOW}Перезапуск Frontend...${NC}"
        docker-compose restart snee-frontend
        echo -e "${GREEN}✓ Frontend перезапущен${NC}"
        sleep 5
        echo "Проверка:"
        curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3001
        ;;
    
    all)
        echo -e "${YELLOW}Перезапуск всех контейнеров...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Все контейнеры перезапущены${NC}"
        sleep 5
        echo ""
        echo "Статус:"
        docker-compose ps
        ;;
    
    *)
        echo "Ошибка: Неизвестная опция '$SERVICE'"
        show_usage
        ;;
esac

echo ""
echo "Для просмотра логов: ./logs.sh $SERVICE"

