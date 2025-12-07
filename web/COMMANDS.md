# 📝 Шпаргалка по командам Docker для SNЭЭ Graf

**Полезные команды для работы с проектом**

---

## 🏗️ Сборка образов (локально)

```powershell
# Windows PowerShell
$env:DOCKER_USERNAME = "your_dockerhub_username"
cd "C:\den\Cursor\SNEE graf\web"

# Backend
docker build -f Dockerfile.backend.prod -t ${env:DOCKER_USERNAME}/snee-backend:latest ..

# Frontend
docker build -f Dockerfile.frontend.prod -t ${env:DOCKER_USERNAME}/snee-frontend:latest ..

# С тегом версии
docker build -f Dockerfile.backend.prod -t ${env:DOCKER_USERNAME}/snee-backend:v1.0 ..
docker build -f Dockerfile.frontend.prod -t ${env:DOCKER_USERNAME}/snee-frontend:v1.0 ..
```

---

## 📤 Push в Docker Hub

```powershell
# Логин
docker login

# Push
docker push ${env:DOCKER_USERNAME}/snee-backend:latest
docker push ${env:DOCKER_USERNAME}/snee-frontend:latest

# Push с версией
docker push ${env:DOCKER_USERNAME}/snee-backend:v1.0
docker push ${env:DOCKER_USERNAME}/snee-frontend:v1.0
```

---

## 🔄 Docker Compose (на сервере)

### Основные команды

```bash
cd /opt/snee-graf

# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Перезапуск с пересозданием
docker-compose up -d --force-recreate

# Остановка одного сервиса
docker-compose stop snee-backend

# Запуск одного сервиса
docker-compose start snee-backend
```

### Обновление

```bash
# Скачать новые образы
docker-compose pull

# Применить обновления
docker-compose up -d --force-recreate

# Удалить старые образы
docker image prune -f
```

---

## 📊 Мониторинг

### Логи

```bash
# Все сервисы (следовать за логами)
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f snee-backend
docker-compose logs -f snee-frontend

# Последние N строк
docker-compose logs --tail=100 snee-backend

# Без следования
docker-compose logs snee-backend
```

### Статус

```bash
# Статус контейнеров
docker-compose ps

# Детальная информация
docker ps --filter "name=snee"

# Использование ресурсов
docker stats

# Использование диска
docker system df
```

---

## 🔧 Отладка

### Вход в контейнер

```bash
# Backend (Python/Bash)
docker exec -it snee-backend /bin/bash

# Frontend (Alpine/sh)
docker exec -it snee-frontend /bin/sh

# Выполнить команду без входа
docker exec snee-backend python --version
```

### Проверка работоспособности

```bash
# API Health Check
curl http://localhost:8001/api/v1/health
curl https://snee.companykd.world/api/v1/health

# Frontend
curl http://localhost:3001
curl https://snee.companykd.world

# Проверка портов
sudo netstat -tulpn | grep :8001
sudo netstat -tulpn | grep :3001
```

### Инспекция

```bash
# Информация о контейнере
docker inspect snee-backend

# IP адрес контейнера
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' snee-backend

# Переменные окружения
docker exec snee-backend env
```

---

## 🗑️ Очистка

### Контейнеры

```bash
# Остановить и удалить контейнеры проекта
docker-compose down

# С удалением volumes
docker-compose down -v

# Удалить все остановленные контейнеры
docker container prune -f
```

### Образы

```bash
# Удалить неиспользуемые образы
docker image prune -a -f

# Удалить конкретный образ
docker rmi your_dockerhub_username/snee-backend:latest

# Удалить все образы SNEE
docker images | grep snee | awk '{print $3}' | xargs docker rmi
```

### Полная очистка

```bash
# ВНИМАНИЕ: Удаляет ВСЕ неиспользуемые ресурсы
docker system prune -a --volumes -f
```

---

## 🌐 Nginx

### Управление

```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка (без разрыва соединений)
sudo systemctl reload nginx

# Перезапуск
sudo systemctl restart nginx

# Остановка
sudo systemctl stop nginx

# Запуск
sudo systemctl start nginx

# Статус
sudo systemctl status nginx
```

### Логи

```bash
# Access логи
sudo tail -f /var/log/nginx/snee-graf-access.log

# Error логи
sudo tail -f /var/log/nginx/snee-graf-error.log

# Последние 50 ошибок
sudo tail -50 /var/log/nginx/snee-graf-error.log

# Поиск ошибок за сегодня
sudo grep "$(date +%Y/%m/%d)" /var/log/nginx/snee-graf-error.log
```

### Тестирование конфигурации

```bash
# Проверка синтаксиса
sudo nginx -t

# Проверка без запуска
sudo nginx -T

# Просмотр активных соединений
sudo netstat -tulpn | grep nginx
```

---

## 🔒 SSL (Let's Encrypt)

```bash
# Получить сертификат
sudo certbot --nginx -d snee.companykd.world

# Обновить все сертификаты
sudo certbot renew

# Обновить с принудительным обновлением
sudo certbot renew --force-renewal

# Тест обновления (без реального обновления)
sudo certbot renew --dry-run

# Список сертификатов
sudo certbot certificates

# Удалить сертификат
sudo certbot delete --cert-name snee.companykd.world
```

---

## 🔍 Диагностика

### Сеть

```bash
# Проверка доступности портов
sudo lsof -i :3001
sudo lsof -i :8001

# Все прослушиваемые порты
sudo ss -tulpn

# Проверка DNS
nslookup snee.companykd.world
dig snee.companykd.world

# Ping
ping snee.companykd.world
```

### Система

```bash
# Использование диска
df -h
du -sh /opt/snee-graf/*
du -sh /var/lib/docker/*

# Использование памяти
free -h
cat /proc/meminfo

# Загрузка CPU
top
htop

# Процессы Docker
ps aux | grep docker
```

### Docker

```bash
# Версия Docker
docker --version
docker-compose --version

# Информация о системе
docker info

# События Docker
docker events

# Сетевые настройки
docker network ls
docker network inspect snee-network
```

---

## 📦 Резервное копирование

### Volumes

```bash
# Список volumes
docker volume ls

# Создание backup volume
docker run --rm -v snee_data:/data -v $(pwd):/backup alpine tar czf /backup/snee-backup.tar.gz /data

# Восстановление из backup
docker run --rm -v snee_data:/data -v $(pwd):/backup alpine tar xzf /backup/snee-backup.tar.gz -C /
```

### Конфигурации

```bash
# Backup всей директории проекта
sudo tar czf /tmp/snee-graf-backup-$(date +%Y%m%d).tar.gz /opt/snee-graf

# Backup Nginx конфигурации
sudo cp /etc/nginx/sites-available/snee-graf /opt/snee-graf/nginx-backup.conf

# Backup SSL сертификатов
sudo tar czf /tmp/ssl-certs-backup.tar.gz /etc/letsencrypt/live/snee.companykd.world/
```

---

## 🚀 Полезные скрипты

### Скрипт полного обновления

```bash
#!/bin/bash
# /opt/snee-graf/update.sh

cd /opt/snee-graf
echo "Pulling latest images..."
docker-compose pull

echo "Recreating containers..."
docker-compose up -d --force-recreate

echo "Cleaning up..."
docker image prune -f

echo "Done! Checking status..."
sleep 3
docker-compose ps
```

### Скрипт проверки статуса

```bash
#!/bin/bash
# /opt/snee-graf/check.sh

echo "=== Docker Status ==="
docker ps --filter "name=snee" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== API Health ==="
curl -s http://localhost:8001/api/v1/health | jq

echo ""
echo "=== Frontend Status ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3001

echo ""
echo "=== Nginx Status ==="
sudo systemctl status nginx --no-pager | head -3

echo ""
echo "=== Recent Errors ==="
docker-compose logs --tail=5 | grep -i error
```

### Скрипт просмотра логов

```bash
#!/bin/bash
# /opt/snee-graf/logs.sh

if [ -z "$1" ]; then
    echo "Usage: $0 [backend|frontend|nginx|all]"
    exit 1
fi

case $1 in
    backend)
        docker-compose logs -f snee-backend
        ;;
    frontend)
        docker-compose logs -f snee-frontend
        ;;
    nginx)
        sudo tail -f /var/log/nginx/snee-graf-error.log
        ;;
    all)
        docker-compose logs -f
        ;;
    *)
        echo "Unknown option: $1"
        exit 1
        ;;
esac
```

Сделайте скрипты исполняемыми:

```bash
chmod +x /opt/snee-graf/*.sh
```

---

## 🔗 Быстрые ссылки

### Локальное тестирование

- Frontend: http://localhost:3001
- Backend API: http://localhost:8001/api/v1/health
- API Docs: http://localhost:8001/docs

### Production

- Frontend: https://snee.companykd.world
- Backend API: https://snee.companykd.world/api/v1/health
- API Docs: https://snee.companykd.world/docs
- ReDoc: https://snee.companykd.world/redoc

### Другой проект на сервере

- CompanyKD: https://companykd.world

---

## 📖 Дополнительная документация

- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Полная инструкция по развертыванию
- [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) - Быстрый старт
- [README.md](README.md) - Общая документация проекта

---

**💡 Совет:** Сохраните эту шпаргалку в закладки для быстрого доступа к командам!

