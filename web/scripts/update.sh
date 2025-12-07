#!/bin/bash

# Скрипт обновления SNЭЭ Graf
# Использование: ./update.sh

echo "╔════════════════════════════════════════════════════╗"
echo "║          SNЭЭ Graf - Обновление проекта           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Переходим в директорию проекта
cd /opt/snee-graf || { echo "Ошибка: Директория /opt/snee-graf не найдена"; exit 1; }

echo -e "${YELLOW}[1/6]${NC} Проверка текущего состояния..."
docker-compose ps
echo ""

echo -e "${YELLOW}[2/6]${NC} Создание backup текущих контейнеров..."
BACKUP_DIR="/opt/snee-graf/backups"
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"

# Backup конфигураций
tar -czf $BACKUP_FILE docker-compose.yml 2>/dev/null
echo -e "${GREEN}✓${NC} Backup создан: $BACKUP_FILE"
echo ""

echo -e "${YELLOW}[3/6]${NC} Загрузка новых образов из Docker Hub..."
docker-compose pull
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Образы успешно загружены"
else
    echo -e "${RED}✗${NC} Ошибка загрузки образов"
    exit 1
fi
echo ""

echo -e "${YELLOW}[4/6]${NC} Пересоздание и перезапуск контейнеров..."
docker-compose up -d --force-recreate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Контейнеры пересозданы"
else
    echo -e "${RED}✗${NC} Ошибка при пересоздании контейнеров"
    exit 1
fi
echo ""

echo -e "${YELLOW}[5/6]${NC} Ожидание запуска сервисов (30 секунд)..."
sleep 30
echo ""

echo -e "${YELLOW}[6/6]${NC} Проверка работоспособности..."
echo ""

# Проверка Backend
echo -n "Backend API: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
fi

# Проверка Frontend
echo -n "Frontend: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
fi
echo ""

echo -e "${YELLOW}[Очистка]${NC} Удаление старых образов..."
docker image prune -f
echo -e "${GREEN}✓${NC} Старые образы удалены"
echo ""

echo "════════════════════════════════════════════════════"
echo -e "${GREEN}Обновление завершено успешно!${NC}"
echo "════════════════════════════════════════════════════"
echo ""
echo "Статус контейнеров:"
docker-compose ps
echo ""
echo "Для просмотра логов: docker-compose logs -f"
echo "Для проверки статуса: ./check-status.sh"
echo ""
echo "Обновлено: $(date)"

