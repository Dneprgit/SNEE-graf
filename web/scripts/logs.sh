#!/bin/bash

# Скрипт для просмотра логов SNЭЭ Graf
# Использование: ./logs.sh [backend|frontend|nginx|all]

show_usage() {
    echo "Использование: $0 [backend|frontend|nginx|all]"
    echo ""
    echo "Опции:"
    echo "  backend   - Логи backend контейнера (FastAPI)"
    echo "  frontend  - Логи frontend контейнера (React)"
    echo "  nginx     - Логи Nginx (access и error)"
    echo "  all       - Логи всех контейнеров"
    echo ""
    echo "Примеры:"
    echo "  $0 backend"
    echo "  $0 all"
    exit 1
}

# Проверка аргументов
if [ -z "$1" ]; then
    show_usage
fi

# Цвета
BLUE='\033[0;34m'
NC='\033[0m'

case $1 in
    backend)
        echo -e "${BLUE}=== Backend Logs (snee-backend) ===${NC}"
        echo "Нажмите Ctrl+C для выхода"
        echo ""
        docker-compose -f /opt/snee-graf/docker-compose.yml logs -f --tail=100 snee-backend
        ;;
    
    frontend)
        echo -e "${BLUE}=== Frontend Logs (snee-frontend) ===${NC}"
        echo "Нажмите Ctrl+C для выхода"
        echo ""
        docker-compose -f /opt/snee-graf/docker-compose.yml logs -f --tail=100 snee-frontend
        ;;
    
    nginx)
        echo -e "${BLUE}=== Nginx Logs ===${NC}"
        echo "Нажмите Ctrl+C для выхода"
        echo ""
        echo "Access log:"
        tail -20 /var/log/nginx/snee-graf-access.log
        echo ""
        echo "Error log:"
        tail -20 /var/log/nginx/snee-graf-error.log
        echo ""
        echo "Following error log..."
        tail -f /var/log/nginx/snee-graf-error.log
        ;;
    
    all)
        echo -e "${BLUE}=== All Container Logs ===${NC}"
        echo "Нажмите Ctrl+C для выхода"
        echo ""
        docker-compose -f /opt/snee-graf/docker-compose.yml logs -f --tail=50
        ;;
    
    *)
        echo "Ошибка: Неизвестная опция '$1'"
        echo ""
        show_usage
        ;;
esac

