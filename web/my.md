
# 🐳 Развертывание SNЭЭ Graf через Docker Hub

**Подробная инструкция по развертыванию проекта на сервере Reg.ru с использованием Docker Hub**

---

## 📋 Оглавление

1. [Предварительные требования](#предварительные-требования)
2. [Часть 1: Подготовка образов локально](#часть-1-подготовка-образов-локально)
3. [Часть 2: Загрузка в Docker Hub](#часть-2-загрузка-в-docker-hub)
4. [Часть 3: Подготовка сервера](#часть-3-подготовка-сервера)
5. [Часть 4: Развертывание на сервере](#часть-4-развертывание-на-сервере)
6. [Часть 5: Настройка Nginx](#часть-5-настройка-nginx)
7. [Часть 6: SSL сертификат](#часть-6-ssl-сертификат)
8. [Часть 7: Автозапуск и мониторинг](#часть-7-автозапуск-и-мониторинг)
9. [Обновление проекта](#обновление-проекта)
10. [Решение проблем](#решение-проблем)

---

## 🎯 Предварительные требования

### На локальном компьютере:
- ✅ Windows с установленным Docker Desktop
- ✅ Аккаунт на [Docker Hub](https://hub.docker.com/)
- ✅ Git для работы с репозиторием

### На сервере (Reg.ru):
- ✅ VPS с Ubuntu 20.04/22.04 или Debian 11/12
- ✅ IP: 194.67.84.241
- ✅ Существующий проект CompanyKD на порту 5000
- ✅ Nginx уже установлен и настроен
- ✅ SSL сертификат от Let's Encrypt настроен для companykd.world

### Информация о портах:
| Сервис | Порт | Назначение |
|--------|------|------------|
| CompanyKD | 5000 | Существующий проект |
| SNEE Backend | 8001 | API сервер |
| SNEE Frontend | 3001 | Веб-интерфейс |

---

## 📦 Часть 1: Подготовка образов локально

### 1.1. Клонирование или обновление репозитория

```powershell
# Переходим в директорию проекта
cd "C:\den\Cursor\SNEE graf"

# Убедитесь, что у вас последняя версия
git pull origin main
```

### 1.2. Проверка структуры проекта

Убедитесь, что у вас есть следующие файлы:
```
SNEE graf/
├── web/
│   ├── backend/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── env.example
│   ├── frontend/
│   │   ├── src/
│   │   ├── package.json
│   │   └── env.example
│   ├── Dockerfile.backend.prod      # ✅ Создан
│   ├── Dockerfile.frontend.prod     # ✅ Создан
│   ├── docker-compose.prod.yml      # ✅ Создан
│   ├── .dockerignore                # ✅ Создан
│   └── nginx-server.conf            # ✅ Создан
├── energy_storage_calculator.py
└── data_manager.py
```

### 1.3. Настройка переменных окружения

#### Backend (.env)
```bash
# Файл уже существует, проверьте его содержимое
# Обычно для продакшена нужны только базовые настройки
ENVIRONMENT=production
```

#### Frontend (.env)
Обновите API URL для продакшена:
```bash
VITE_API_URL=https://snee.companykd.world/api
```

### 1.4. Сборка Docker образов

Откройте PowerShell в директории проекта:

```powershell
#1 Переходим в папку web
cd web

# Устанавливаем переменную с вашим Docker Hub username
$env:DOCKER_USERNAME = "your_dockerhub_username"

# Собираем Backend образ
docker build -f Dockerfile.backend.prod -t ${env:DOCKER_USERNAME}/snee-backend:latest ..
#2 Собираем Backend образ
docker build -f Dockerfile.backend.prod -t end2040/snee-backend:latest ..

docker build -f Dockerfile.backend.prod -t end2040/snee_web_spes-backend:latest .

# Собираем Frontend образ
docker build -f Dockerfile.frontend.prod -t ${env:DOCKER_USERNAME}/snee-frontend:latest ..

#3 Собираем Frontend образ
docker build -f Dockerfile.frontend.prod -t end2040/snee-frontend:latest ..
```
docker build -f Dockerfile.frontend.prod -t end2040/snee_web_spes-frontend:latest .

**Примечание:** Замените `your_dockerhub_username` на ваше имя пользователя в Docker Hub.

### 1.5. Тестирование образов локально (опционально)

```powershell
# Тест Backend
docker run -d -p 8001:8001 --name test-backend ${env:DOCKER_USERNAME}/snee-backend:latest
# Тест Backend
docker run -d -p 8001:8001 --name test-backend end2040/snee-backend:latest

docker run -d -p 8002:8002 --name test-backend2 end2040/snee_web_spes-backend:latest
# Проверка
curl http://localhost:8001/api/v1/health

# Остановка
docker stop test-backend
docker rm test-backend

# Тест Frontend
docker run -d -p 3001:80 --name test-frontend ${env:DOCKER_USERNAME}/snee-frontend:latest
# Тест Frontend
docker run -d -p 3001:80 --name test-frontend end2040/snee-frontend:latest

docker run -d -p 3002:80 --name test-frontend2 end2040/snee_web_spes-frontend:latest
# Откройте в браузере: http://localhost:3001

# Остановка
docker stop test-frontend
docker rm test-frontend
```

---

## 🚀 Часть 2: Загрузка в Docker Hub

### 2.1. Вход в Docker Hub

```powershell
docker login
```

Введите ваш username и password от Docker Hub.

### 2.2. Push образов в Docker Hub

```powershell
# Push Backend
docker push ${env:DOCKER_USERNAME}/snee-backend:latest
 Push Backend
docker push end2040/snee-backend:latest
# Push Frontend
docker push ${env:DOCKER_USERNAME}/snee-frontend:latest
# Push Frontend
docker push end2040/snee-frontend:latest

docker push end2040/snee_web_spes-frontend:latest
```

### 2.3. Проверка на Docker Hub

1. Перейдите на https://hub.docker.com/
2. Войдите в свой аккаунт
3. Убедитесь, что оба репозитория созданы:
   - `your_dockerhub_username/snee-backend`
   - `your_dockerhub_username/snee-frontend`

### 2.4. Сделайте репозитории публичными (опционально)

Если вы хотите, чтобы образы были доступны без авторизации:
1. Зайдите в настройки каждого репозитория
2. Settings → Visibility → Public

---

## 🖥️ Часть 3: Подготовка сервера

### 3.1. Подключение к серверу по SSH

```powershell
# Из Windows PowerShell
ssh root@194.67.84.241
```

### 3.2. Обновление системы

```bash
# Обновляем пакеты
sudo apt update && sudo apt upgrade -y
```

### 3.3. Проверка установки Docker

```bash
# Проверяем версию Docker
docker --version

# Проверяем запущенные контейнеры (CompanyKD должен быть там)
docker ps

# Проверяем Docker Compose
docker-compose --version
```

Если Docker не установлен:
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose -y
```

### 3.4. Создание директории для проекта

```bash
# Создаем директорию для SNEE Graf
sudo mkdir -p /opt/snee-graf
cd /opt/snee-graf
```

---

## 📥 Часть 4: Развертывание на сервере

### 4.1. Создание docker-compose.yml на сервере

```bash
# Создаем файл
nano docker-compose.yml
```

Вставьте следующее содержимое (замените `your_dockerhub_username`):

```yaml
version: '3.8'

services:
  snee-backend:
    image: your_dockerhub_username/snee-backend:latest
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
    image: your_dockerhub_username/snee-frontend:latest
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
```

Сохраните файл: `Ctrl+X`, затем `Y`, затем `Enter`.

### 4.2. Загрузка образов с Docker Hub

```bash
# Pull образов
docker-compose pull
```

### 4.3. Запуск контейнеров

```bash
# Запуск в detached режиме
docker-compose up -d
```

### 4.4. Проверка запуска

```bash
# Проверяем статус контейнеров
docker-compose ps

# Должно быть примерно так:
#      Name                    State           Ports
# -------------------------------------------------------------
# snee-backend     Up         0.0.0.0:8001->8001/tcp
# snee-frontend    Up         0.0.0.0:3001->80/tcp

# Смотрим логи
docker-compose logs -f

# Для выхода из логов: Ctrl+C
```

### 4.5. Тестирование API

```bash
# Проверяем health endpoint
curl http://localhost:8001/api/v1/health

# Должен вернуть: {"status":"ok"}

# Проверяем frontend
curl http://localhost:3001

# Должен вернуть HTML
```

---

## 🌐 Часть 5: Настройка Nginx

### 5.1. Создание конфигурации для SNEE Graf

```bash
# Создаем конфиг файл
sudo nano /etc/nginx/sites-available/snee-graf
```

Вставьте следующую конфигурацию:

```nginx
# Upstream для backend
upstream snee_backend {
    server 127.0.0.1:8001;
}

# Upstream для frontend
upstream snee_frontend {
    server 127.0.0.1:3001;
}

# HTTP сервер - редирект на HTTPS (будет настроен после SSL)
server {
    listen 80;
    listen [::]:80;
    server_name snee.companykd.world;

    # Для Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Временно разрешаем HTTP для тестирования
    # После настройки SSL раскомментируйте редирект ниже
    # return 301 https://$server_name$request_uri;

    # Логи
    access_log /var/log/nginx/snee-graf-access.log;
    error_log /var/log/nginx/snee-graf-error.log;

    # Размер загружаемых файлов (для Excel)
    client_max_body_size 10M;

    # Backend API
    location /api {
        proxy_pass http://snee_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API документация
    location /docs {
        proxy_pass http://snee_backend/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://snee_backend/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://snee_backend/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend
    location / {
        proxy_pass http://snee_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json image/svg+xml;
}
```

Сохраните файл: `Ctrl+X`, `Y`, `Enter`.

### 5.2. Активация конфигурации

```bash
# Создаем символическую ссылку
sudo ln -s /etc/nginx/sites-available/snee-graf /etc/nginx/sites-enabled/

# Проверяем конфигурацию на ошибки
sudo nginx -t

# Перезагружаем Nginx
sudo systemctl reload nginx
```

### 5.3. Настройка DNS (если нужен поддомен)

Если вы хотите использовать поддомен `snee.companykd.world`:

1. Зайдите в панель управления доменом на Reg.ru
2. Добавьте A-запись:
   - **Имя**: `snee`
   - **Тип**: `A`
   - **Значение**: `194.67.84.241`
   - **TTL**: `3600`

3. Дождитесь распространения DNS (5-30 минут)

Проверка DNS:
```bash
# На локальном компьютере
nslookup snee.companykd.world
```

### 5.4. Тестирование через HTTP

```bash
# С сервера
curl http://snee.companykd.world/api/v1/health

# С локального компьютера в браузере:
# http://snee.companykd.world
```

---

## 🔒 Часть 6: SSL сертификат

### 6.1. Установка Certbot (если еще не установлен)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y
```

### 6.2. Получение SSL сертификата

```bash
# Получаем сертификат для поддомена
sudo certbot --nginx -d snee.companykd.world
```

Следуйте инструкциям:
1. Введите email для уведомлений
2. Согласитесь с условиями (Y)
3. Выберите, хотите ли вы перенаправлять HTTP на HTTPS (рекомендуется: 2)

### 6.3. Обновление конфигурации Nginx для HTTPS

Certbot автоматически обновит конфигурацию. Проверьте:

```bash
sudo nano /etc/nginx/sites-available/snee-graf
```

Должны появиться блоки с SSL настройками. Если нет, добавьте вручную:

```nginx
# HTTPS сервер
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name snee.companykd.world;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/snee.companykd.world/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/snee.companykd.world/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/snee.companykd.world/chain.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Логи
    access_log /var/log/nginx/snee-graf-access.log;
    error_log /var/log/nginx/snee-graf-error.log;

    # Размер загружаемых файлов
    client_max_body_size 10M;

    # Backend API
    location /api {
        proxy_pass http://snee_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API документация
    location /docs {
        proxy_pass http://snee_backend/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://snee_backend/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://snee_backend/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend
    location / {
        proxy_pass http://snee_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json image/svg+xml;
}

# Редирект HTTP на HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name snee.companykd.world;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

### 6.4. Перезагрузка Nginx

```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка
sudo systemctl reload nginx
```

### 6.5. Автообновление сертификатов

```bash
# Проверка автообновления
sudo certbot renew --dry-run

# Certbot автоматически настроит cron job для обновления
```

### 6.6. Тестирование HTTPS

```bash
# С сервера
curl https://snee.companykd.world/api/v1/health

# В браузере:
# https://snee.companykd.world
```

---

## ⚙️ Часть 7: Автозапуск и мониторинг

### 7.1. Проверка автозапуска Docker

```bash
# Проверяем, что Docker запускается при загрузке системы
sudo systemctl is-enabled docker

# Если нет, включаем
sudo systemctl enable docker
```

### 7.2. Настройка автозапуска контейнеров

В нашем `docker-compose.yml` уже указан `restart: always`, поэтому контейнеры будут автоматически перезапускаться.

Проверка:
```bash
# Перезагружаем сервер
sudo reboot

# После перезагрузки, подключаемся снова и проверяем
ssh root@194.67.84.241
docker ps

# Контейнеры должны быть запущены
```

### 7.3. Мониторинг логов

```bash
# Просмотр логов всех контейнеров
cd /opt/snee-graf
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f snee-backend
docker-compose logs -f snee-frontend

# Логи Nginx
sudo tail -f /var/log/nginx/snee-graf-access.log
sudo tail -f /var/log/nginx/snee-graf-error.log
```

### 7.4. Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Использование диска
df -h

# Использование памяти
free -h
```

### 7.5. Скрипт для быстрой проверки статуса

Создайте скрипт для проверки:

```bash
nano /opt/snee-graf/check-status.sh
```

Вставьте:

```bash
#!/bin/bash
echo "=== Docker Containers Status ==="
docker ps --filter "name=snee" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== Health Checks ==="
echo -n "Backend API: "
curl -s http://localhost:8001/api/v1/health | jq -r .status 2>/dev/null || echo "FAILED"

echo -n "Frontend: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q 200 && echo "OK" || echo "FAILED"

echo ""
echo "=== Nginx Status ==="
sudo systemctl status nginx | grep Active

echo ""
echo "=== Recent Errors in Logs (last 5) ==="
echo "Backend errors:"
docker logs snee-backend 2>&1 | grep -i error | tail -5

echo "Frontend errors:"
docker logs snee-frontend 2>&1 | grep -i error | tail -5
```

Сделайте скрипт исполняемым:

```bash
chmod +x /opt/snee-graf/check-status.sh
```

Использование:

```bash
/opt/snee-graf/check-status.sh
```

---

## 🔄 Обновление проекта

### Когда нужно обновить приложение:

### На локальном компьютере:

```powershell
# 1. Вносим изменения в код
# 2. Пересобираем образы
cd "C:\den\Cursor\SNEE graf\web"
$env:DOCKER_USERNAME = "your_dockerhub_username"

# Пересборка с новым тегом (версией)
docker build -f Dockerfile.backend.prod -t ${env:DOCKER_USERNAME}/snee-backend:v1.1 ..
docker build -f Dockerfile.frontend.prod -t ${env:DOCKER_USERNAME}/snee-frontend:v1.1 ..

# Также обновляем latest
docker tag ${env:DOCKER_USERNAME}/snee-backend:v1.1 ${env:DOCKER_USERNAME}/snee-backend:latest
docker tag ${env:DOCKER_USERNAME}/snee-frontend:v1.1 ${env:DOCKER_USERNAME}/snee-frontend:latest

# Push в Docker Hub
docker push ${env:DOCKER_USERNAME}/snee-backend:v1.1
docker push ${env:DOCKER_USERNAME}/snee-backend:latest
docker push ${env:DOCKER_USERNAME}/snee-frontend:v1.1
docker push ${env:DOCKER_USERNAME}/snee-frontend:latest
```

### На сервере:

```bash
# Переходим в директорию проекта
cd /opt/snee-graf

# Скачиваем новые образы
docker-compose pull

# Пересоздаем и перезапускаем контейнеры
docker-compose up -d --force-recreate

# Удаляем старые образы (опционально)
docker image prune -f
```

### Скрипт автоматического обновления:

```bash
nano /opt/snee-graf/update.sh
```

Вставьте:

```bash
#!/bin/bash
echo "=== Updating SNEE Graf ==="

cd /opt/snee-graf

echo "Pulling latest images..."
docker-compose pull

echo "Recreating containers..."
docker-compose up -d --force-recreate

echo "Cleaning up old images..."
docker image prune -f

echo "=== Update complete ==="
echo "Checking status..."
sleep 5
./check-status.sh
```

Сделайте исполняемым:

```bash
chmod +x /opt/snee-graf/update.sh
```

---

## 🐛 Решение проблем

### Проблема: Контейнер не запускается

```bash
# Смотрим логи
docker-compose logs snee-backend
docker-compose logs snee-frontend

# Проверяем, не занят ли порт
sudo netstat -tulpn | grep :8001
sudo netstat -tulpn | grep :8000

# Перезапускаем контейнеры
docker-compose restart
```

### Проблема: 502 Bad Gateway от Nginx

```bash
# Проверяем, запущены ли контейнеры
docker ps

# Проверяем логи Nginx
sudo tail -f /var/log/nginx/snee-graf-error.log

# Проверяем, слушают ли контейнеры на портах
curl http://localhost:8001/api/v1/health
curl http://localhost:8000

# Перезапускаем Nginx
sudo systemctl restart nginx
```

### Проблема: Недостаточно памяти

```bash
# Проверяем использование памяти
docker stats

# Ограничиваем память для контейнеров
# Добавьте в docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M

# Перезапускаем с новыми лимитами
docker-compose up -d --force-recreate
```

### Проблема: SSL сертификат не работает

```bash
# Проверяем сертификаты
sudo certbot certificates

# Обновляем сертификат
sudo certbot renew --force-renewal

# Перезапускаем Nginx
sudo systemctl restart nginx
```

### Проблема: Контейнеры съедают много места на диске

```bash
# Проверяем использование диска
df -h
docker system df

# Очищаем неиспользуемые образы, контейнеры и volumes
docker system prune -a --volumes

# ВНИМАНИЕ: Это удалит все неиспользуемые данные!
# Используйте с осторожностью
```

### Проблема: Не работает загрузка Excel файлов

```bash
# Проверьте настройку client_max_body_size в Nginx
sudo nano /etc/nginx/sites-available/snee-graf

# Должно быть:
# client_max_body_size 10M;

# Перезагрузите Nginx
sudo systemctl reload nginx
```

---

## 📊 Полезные команды

### Docker

```bash
# Список всех контейнеров
docker ps -a

# Остановка всех контейнеров проекта
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Перезапуск одного контейнера
docker-compose restart snee-backend

# Просмотр логов за последние 100 строк
docker-compose logs --tail=100 snee-backend

# Вход в контейнер
docker exec -it snee-backend /bin/bash
```

### Nginx

```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка (без разрыва соединений)
sudo systemctl reload nginx

# Перезапуск (с разрывом соединений)
sudo systemctl restart nginx

# Просмотр статуса
sudo systemctl status nginx

# Просмотр активных соединений
sudo netstat -tulpn | grep nginx
```

### Система

```bash
# Мониторинг ресурсов
htop

# Использование диска
du -sh /opt/snee-graf/*

# Сетевые соединения
ss -tulpn

# Проверка портов
sudo lsof -i :3001
sudo lsof -i :8001
```

---

## ✅ Чек-лист развертывания

- [ ] Локально собраны и протестированы Docker образы
- [ ] Образы загружены в Docker Hub
- [ ] На сервере установлен Docker и Docker Compose
- [ ] Создан docker-compose.yml на сервере
- [ ] Контейнеры запущены и работают
- [ ] API отвечает на health check
- [ ] Frontend открывается в браузере
- [ ] Nginx настроен и работает
- [ ] DNS записи настроены (если используется поддомен)
- [ ] SSL сертификат получен и настроен
- [ ] HTTPS работает без ошибок
- [ ] Автозапуск контейнеров настроен
- [ ] Логирование настроено
- [ ] Создан скрипт для обновления
- [ ] Создан скрипт для проверки статуса
- [ ] Проведено тестирование всех функций

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи контейнеров: `docker-compose logs`
2. Проверьте логи Nginx: `sudo tail -f /var/log/nginx/snee-graf-error.log`
3. Запустите скрипт проверки: `/opt/snee-graf/check-status.sh`
4. Проверьте документацию: [Docker Docs](https://docs.docker.com/)

---

**🎉 Поздравляем! Ваш проект SNЭЭ Graf успешно развернут в продакшен!**

**Адреса доступа:**
- Frontend: https://snee.companykd.world
- API: https://snee.companykd.world/api/v1/health
- API Docs: https://snee.companykd.world/docs

