# 🚀 Быстрый старт - Docker Deployment

**Краткая инструкция для быстрого развертывания SNЭЭ Graf**

---

## 📋 Предварительные требования

- Docker Desktop на Windows
- Аккаунт Docker Hub
- SSH доступ к серверу

---

## ⚡ Локально (Windows)

### 1. Сборка и Push образов

```powershell
# Установите ваш Docker Hub username
$env:DOCKER_USERNAME = "your_dockerhub_username"

# Перейдите в папку web
cd "C:\den\Cursor\SNEE graf\web"

# Соберите образы
docker build -f Dockerfile.backend.prod -t ${env:DOCKER_USERNAME}/snee-backend:latest ..
docker build -f Dockerfile.frontend.prod -t ${env:DOCKER_USERNAME}/snee-frontend:latest ..

# Войдите в Docker Hub
docker login

# Push образов
docker push ${env:DOCKER_USERNAME}/snee-backend:latest
docker push ${env:DOCKER_USERNAME}/snee-frontend:latest
```

---

## 🖥️ На сервере

### 1. Подключение и подготовка

```bash
# Подключитесь к серверу
ssh root@194.67.84.241

# Создайте директорию
sudo mkdir -p /opt/snee-graf && cd /opt/snee-graf
```

### 2. Создайте docker-compose.yml

```bash
nano docker-compose.yml
```

Вставьте (замените `your_dockerhub_username`):

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

networks:
  snee-network:
    driver: bridge
```

### 3. Запустите контейнеры

```bash
docker-compose pull
docker-compose up -d
docker-compose ps
```

### 4. Настройте Nginx

```bash
sudo nano /etc/nginx/sites-available/snee-graf
```

Вставьте минимальную конфигурацию:

```nginx
upstream snee_backend {
    server 127.0.0.1:8001;
}

upstream snee_frontend {
    server 127.0.0.1:3001;
}

server {
    listen 80;
    server_name snee.companykd.world;

    client_max_body_size 10M;

    location /api {
        proxy_pass http://snee_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /docs {
        proxy_pass http://snee_backend/docs;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://snee_backend/redoc;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://snee_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Активируйте:

```bash
sudo ln -s /etc/nginx/sites-available/snee-graf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL сертификат

```bash
sudo certbot --nginx -d snee.companykd.world
```

---

## ✅ Проверка

```bash
# API
curl https://snee.companykd.world/api/v1/health

# Frontend в браузере
https://snee.companykd.world
```

---

## 🔄 Обновление

### Локально:

```powershell
# Пересоберите и push образы
docker build -f Dockerfile.backend.prod -t ${env:DOCKER_USERNAME}/snee-backend:latest ..
docker push ${env:DOCKER_USERNAME}/snee-backend:latest

docker build -f Dockerfile.frontend.prod -t ${env:DOCKER_USERNAME}/snee-frontend:latest ..
docker push ${env:DOCKER_USERNAME}/snee-frontend:latest
```

### На сервере:

```bash
cd /opt/snee-graf
docker-compose pull
docker-compose up -d --force-recreate
```

---

## 🐛 Устранение неполадок

```bash
# Логи
docker-compose logs -f

# Статус контейнеров
docker-compose ps

# Перезапуск
docker-compose restart

# Полная переустановка
docker-compose down
docker-compose up -d
```

---

## 📚 Полная документация

См. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) для подробной информации.

---

**Готово! Ваш проект развернут! 🎉**

