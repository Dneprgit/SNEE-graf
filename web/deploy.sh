#!/bin/bash
# Скрипт для быстрого развертывания SNEE Graf в Docker

set -e  # Остановка при ошибке

echo "🐳 SNEE Graf Docker Deployment Script"
echo "======================================"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Проверка Docker
echo ""
echo "Проверка требований..."
if ! command -v docker &> /dev/null; then
    error "Docker не установлен!"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
success "Docker установлен"

if ! command -v docker compose &> /dev/null; then
    error "Docker Compose не установлен!"
    echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
success "Docker Compose установлен"

# Выбор типа развертывания
echo ""
echo "Выберите тип развертывания:"
echo "1) Development (simple)"
echo "2) Production (with SSL and nginx)"
read -p "Ваш выбор (1/2): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Development развертывание"
        COMPOSE_FILE="docker-compose.yml"
        ;;
    2)
        echo ""
        echo "🚀 Production развертывание"
        COMPOSE_FILE="docker-compose.prod.yml"
        
        # Проверка .env.production
        if [ ! -f ".env.production" ]; then
            warning ".env.production не найден"
            read -p "Создать из примера? (y/n): " create_env
            if [ "$create_env" == "y" ]; then
                cp .env.production.example .env.production
                warning "Отредактируйте .env.production перед продолжением!"
                read -p "Нажмите Enter после редактирования..."
            else
                error "Необходим файл .env.production"
                exit 1
            fi
        fi
        success ".env.production найден"
        
        # Проверка SSL сертификатов
        if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
            warning "SSL сертификаты не найдены в nginx/ssl/"
            read -p "Создать self-signed сертификат для тестирования? (y/n): " create_ssl
            if [ "$create_ssl" == "y" ]; then
                mkdir -p nginx/ssl
                openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                    -keyout nginx/ssl/key.pem \
                    -out nginx/ssl/cert.pem \
                    -subj "/CN=localhost"
                success "Self-signed сертификат создан"
                warning "Для продакшина используйте настоящие SSL сертификаты!"
            else
                error "Скопируйте SSL сертификаты в nginx/ssl/"
                exit 1
            fi
        fi
        success "SSL сертификаты найдены"
        ;;
    *)
        error "Неверный выбор"
        exit 1
        ;;
esac

# Создание необходимых директорий
echo ""
echo "Создание директорий..."
mkdir -p data logs/backend logs/nginx
success "Директории созданы"

# Остановка существующих контейнеров
echo ""
echo "Остановка существующих контейнеров..."
docker compose -f $COMPOSE_FILE down 2>/dev/null || true
success "Существующие контейнеры остановлены"

# Build images
echo ""
echo "Building Docker images..."
docker compose -f $COMPOSE_FILE build
success "Images собраны"

# Запуск контейнеров
echo ""
echo "Запуск контейнеров..."
docker compose -f $COMPOSE_FILE up -d
success "Контейнеры запущены"

# Ожидание готовности
echo ""
echo "Ожидание готовности сервисов..."
sleep 5

# Проверка статуса
echo ""
echo "Проверка статуса контейнеров..."
docker compose -f $COMPOSE_FILE ps

# Health checks
echo ""
echo "Проверка health checks..."
sleep 10

# Backend health check
if curl -s http://localhost:8002/api/v1/health > /dev/null; then
    success "Backend работает"
else
    error "Backend не отвечает"
    echo "Проверьте логи: docker compose -f $COMPOSE_FILE logs backend"
fi

# Frontend health check
if [ "$choice" == "1" ]; then
    if curl -s http://localhost/health > /dev/null 2>&1 || curl -s http://localhost > /dev/null 2>&1; then
        success "Frontend работает"
    else
        error "Frontend не отвечает"
        echo "Проверьте логи: docker compose -f $COMPOSE_FILE logs frontend"
    fi
else
    if curl -s http://localhost/health > /dev/null 2>&1; then
        success "Nginx работает"
    else
        warning "Nginx может быть недоступен (проверьте порты и SSL)"
    fi
fi

# Итоговая информация
echo ""
echo "======================================"
echo "✅ Развертывание завершено!"
echo "======================================"
echo ""

if [ "$choice" == "1" ]; then
    echo "📱 Frontend: http://localhost"
    echo "🔧 Backend API: http://localhost:8002"
    echo "📊 API Docs: http://localhost:8002/docs"
else
    echo "📱 Frontend: https://localhost"
    echo "🔧 Backend API: https://localhost:8002"
    echo "📊 API Docs: https://localhost:8002/docs"
fi

echo ""
echo "📝 Полезные команды:"
echo "   docker compose -f $COMPOSE_FILE ps           # Статус"
echo "   docker compose -f $COMPOSE_FILE logs -f      # Логи"
echo "   docker compose -f $COMPOSE_FILE restart      # Перезапуск"
echo "   docker compose -f $COMPOSE_FILE down         # Остановка"
echo ""

# Предложение просмотреть логи
read -p "Показать логи? (y/n): " show_logs
if [ "$show_logs" == "y" ]; then
    docker compose -f $COMPOSE_FILE logs -f
fi

