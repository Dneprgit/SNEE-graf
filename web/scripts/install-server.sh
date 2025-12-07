#!/bin/bash

# Скрипт первоначальной установки SNЭЭ Graf на сервер
# Использование: curl -sSL https://your-repo/install-server.sh | bash
# Или: ./install-server.sh

set -e  # Выход при ошибке

echo "╔════════════════════════════════════════════════════╗"
echo "║      SNЭЭ Graf - Установка на сервер Reg.ru       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Ошибка: Запустите скрипт с правами root (sudo)${NC}"
    exit 1
fi

# Запрос Docker Hub username
echo -e "${YELLOW}Введите ваш Docker Hub username:${NC}"
read -p "Username: " DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED}Ошибка: Username не может быть пустым${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[1/8]${NC} Обновление системы..."
apt update && apt upgrade -y
echo -e "${GREEN}✓${NC} Система обновлена"
echo ""

echo -e "${YELLOW}[2/8]${NC} Проверка установки Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓${NC} Docker установлен"
else
    echo -e "${GREEN}✓${NC} Docker уже установлен"
fi
echo ""

echo -e "${YELLOW}[3/8]${NC} Проверка установки Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose не установлен. Устанавливаем..."
    apt install docker-compose -y
    echo -e "${GREEN}✓${NC} Docker Compose установлен"
else
    echo -e "${GREEN}✓${NC} Docker Compose уже установлен"
fi
echo ""

echo -e "${YELLOW}[4/8]${NC} Создание директории проекта..."
mkdir -p /opt/snee-graf/backups
mkdir -p /opt/snee-graf/scripts
cd /opt/snee-graf
echo -e "${GREEN}✓${NC} Директория создана: /opt/snee-graf"
echo ""

echo -e "${YELLOW}[5/8]${NC} Создание docker-compose.yml..."
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  snee-backend:
    image: ${DOCKER_USERNAME}/snee-backend:latest
    container_name: snee-backend
    restart: always
    ports:
      - "8001:8001"
    environment:
      - PYTHONUNBUFFERED=1
      - ENVIRONMENT=production
    networks:
      - snee-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  snee-frontend:
    image: ${DOCKER_USERNAME}/snee-frontend:latest
    container_name: snee-frontend
    restart: always
    ports:
      - "3001:80"
    networks:
      - snee-network
    depends_on:
      - snee-backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

networks:
  snee-network:
    driver: bridge
EOF
echo -e "${GREEN}✓${NC} docker-compose.yml создан"
echo ""

echo -e "${YELLOW}[6/8]${NC} Загрузка образов из Docker Hub..."
docker-compose pull
echo -e "${GREEN}✓${NC} Образы загружены"
echo ""

echo -e "${YELLOW}[7/8]${NC} Запуск контейнеров..."
docker-compose up -d
echo -e "${GREEN}✓${NC} Контейнеры запущены"
echo ""

echo "Ожидание запуска сервисов (30 секунд)..."
sleep 30
echo ""

echo -e "${YELLOW}[8/8]${NC} Проверка работоспособности..."
echo ""

# Backend check
echo -n "Backend API: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
fi

# Frontend check
echo -n "Frontend: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
fi
echo ""

echo "════════════════════════════════════════════════════"
echo -e "${GREEN}Установка завершена успешно!${NC}"
echo "════════════════════════════════════════════════════"
echo ""
echo "Контейнеры:"
docker-compose ps
echo ""
echo "Следующие шаги:"
echo "1. Настройте Nginx (см. документацию)"
echo "2. Получите SSL сертификат"
echo "3. Настройте DNS записи"
echo ""
echo "Полная документация: /opt/snee-graf/README_DOCKER.md"
echo ""
echo "Полезные команды:"
echo "  Логи:        docker-compose logs -f"
echo "  Статус:      docker-compose ps"
echo "  Перезапуск:  docker-compose restart"
echo "  Остановка:   docker-compose down"
echo ""

