#!/bin/bash

# Скрипт проверки статуса SNЭЭ Graf
# Использование: ./check-status.sh

echo "╔════════════════════════════════════════════════════╗"
echo "║       SNЭЭ Graf - Проверка статуса системы        ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки с цветным выводом
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# 1. Проверка Docker
echo "═══ Docker ═══"
docker --version > /dev/null 2>&1
check_status $? "Docker установлен"

docker ps > /dev/null 2>&1
check_status $? "Docker daemon запущен"
echo ""

# 2. Статус контейнеров
echo "═══ Контейнеры ═══"
docker ps --filter "name=snee" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 3. Health checks контейнеров
echo "═══ Health Checks ═══"

# Backend
if docker ps | grep -q "snee-backend"; then
    BACKEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' snee-backend 2>/dev/null)
    if [ "$BACKEND_HEALTH" == "healthy" ] || [ -z "$BACKEND_HEALTH" ]; then
        echo -e "${GREEN}✓${NC} Backend контейнер: Running"
    else
        echo -e "${RED}✗${NC} Backend контейнер: $BACKEND_HEALTH"
    fi
else
    echo -e "${RED}✗${NC} Backend контейнер: Not running"
fi

# Frontend
if docker ps | grep -q "snee-frontend"; then
    FRONTEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' snee-frontend 2>/dev/null)
    if [ "$FRONTEND_HEALTH" == "healthy" ] || [ -z "$FRONTEND_HEALTH" ]; then
        echo -e "${GREEN}✓${NC} Frontend контейнер: Running"
    else
        echo -e "${RED}✗${NC} Frontend контейнер: $FRONTEND_HEALTH"
    fi
else
    echo -e "${RED}✗${NC} Frontend контейнер: Not running"
fi
echo ""

# 4. API проверки
echo "═══ API Endpoints ═══"

# Health check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health 2>/dev/null)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓${NC} Backend API (/api/v1/health): HTTP $HTTP_CODE"
else
    echo -e "${RED}✗${NC} Backend API (/api/v1/health): HTTP $HTTP_CODE"
fi

# Frontend
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend (http://localhost:3001): HTTP $HTTP_CODE"
else
    echo -e "${RED}✗${NC} Frontend (http://localhost:3001): HTTP $HTTP_CODE"
fi
echo ""

# 5. Nginx статус
echo "═══ Nginx ═══"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓${NC} Nginx: Active"
    
    # Проверяем конфигурацию
    if nginx -t > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Nginx конфигурация: OK"
    else
        echo -e "${RED}✗${NC} Nginx конфигурация: Есть ошибки"
    fi
else
    echo -e "${RED}✗${NC} Nginx: Inactive"
fi
echo ""

# 6. Использование ресурсов
echo "═══ Использование ресурсов ═══"

# CPU и Memory
if command -v docker &> /dev/null; then
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep snee
fi
echo ""

# Диск
echo "Использование диска:"
df -h / | tail -1 | awk '{print "Использовано: "$3" из "$2" ("$5")"}'
echo ""

# 7. SSL сертификаты (если установлен certbot)
if command -v certbot &> /dev/null; then
    echo "═══ SSL Сертификаты ═══"
    CERT_INFO=$(certbot certificates 2>/dev/null | grep -A 3 "snee.companykd.world" | grep "Expiry Date")
    if [ ! -z "$CERT_INFO" ]; then
        echo -e "${GREEN}✓${NC} SSL сертификат найден"
        echo "$CERT_INFO"
    else
        echo -e "${YELLOW}!${NC} SSL сертификат не найден"
    fi
    echo ""
fi

# 8. Последние ошибки в логах
echo "═══ Последние ошибки (последние 5) ═══"

echo "Backend errors:"
docker logs snee-backend --tail 50 2>&1 | grep -i "error" | tail -5 | while read line; do
    echo -e "${RED}→${NC} $line"
done || echo "Нет ошибок"

echo ""
echo "Frontend errors:"
docker logs snee-frontend --tail 50 2>&1 | grep -i "error" | tail -5 | while read line; do
    echo -e "${RED}→${NC} $line"
done || echo "Нет ошибок"

echo ""
echo "Nginx errors:"
if [ -f /var/log/nginx/snee-graf-error.log ]; then
    tail -5 /var/log/nginx/snee-graf-error.log | while read line; do
        echo -e "${RED}→${NC} $line"
    done || echo "Нет ошибок"
else
    echo "Лог файл не найден"
fi

echo ""
echo "════════════════════════════════════════════════════"
echo "Проверка завершена: $(date)"
echo "════════════════════════════════════════════════════"

