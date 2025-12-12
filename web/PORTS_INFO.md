# 🔌 Информация о портах SNЭЭ Graf

## 📊 Схема портов

### Локальная разработка (без Docker)
```
Backend:   http://localhost:8002
Frontend:  http://localhost:3002
```

### Production на сервере
```
Backend:   http://localhost:8002
Frontend:  http://localhost:3002

Через домен (с Nginx + SSL):
https://so-spes.ru
https://www.so-spes.ru
```

---

## 🐳 Docker контейнеры

### Внутренние порты контейнеров
```
snee-backend:   порт 8002 внутри контейнера
snee-frontend:  порт 80 внутри контейнера (Nginx)
```

### Проброс портов (host:container)
```
Backend:   8002:8002
Frontend:  3002:80
```

**Docker Hub репозиторий:**
```
end2040/snee_web_spes-backend:latest
end2040/snee_web_spes-frontend:latest
```

**Команда в docker-compose.server.yml:**
```yaml
services:
  snee-backend:
    image: end2040/snee_web_spes-backend:latest
    ports:
      - "8002:8002"
  
  snee-frontend:
    image: end2040/snee_web_spes-frontend:latest
    ports:
      - "3002:80"
```

---

## 🌐 Nginx конфигурация

### Upstreams
```nginx
upstream snee_backend {
    server 127.0.0.1:8002;
}

upstream snee_frontend {
    server 127.0.0.1:3002;
}
```

### Locations
```nginx
server {
    listen 443 ssl http2;
    server_name so-spes.ru www.so-spes.ru;
    
    # Frontend
    location / {
        proxy_pass http://snee_frontend;  # → 127.0.0.1:3002
    }
    
    # Backend API
    location /api {
        proxy_pass http://snee_backend;    # → 127.0.0.1:8002
    }
}
```

---

## 🔄 Поток запросов

### Пользователь → Приложение

```
1. Пользователь открывает:
   https://so-spes.ru

2. Nginx получает запрос на порту 443 (HTTPS)

3. Nginx проксирует на frontend контейнер:
   127.0.0.1:3002 (Docker порт snee-frontend)

4. Frontend отдает React приложение

5. React приложение делает API запросы:
   https://so-spes.ru/api/v1/...

6. Nginx проксирует API запросы на backend:
   127.0.0.1:8002 (Docker порт snee-backend)

7. Backend обрабатывает и возвращает результат
```

### Схема
```
Браузер
   ↓ HTTPS (443)
Nginx (SSL терминация)
   ↓
   ├─→ / (frontend) → 127.0.0.1:3002 → Docker snee-frontend
   └─→ /api         → 127.0.0.1:8002 → Docker snee-backend
```

---

## ✅ Проверка портов

### На сервере

```bash
# Проверка, что порты слушаются
sudo netstat -tulpn | grep :8002
sudo netstat -tulpn | grep :3002
sudo netstat -tulpn | grep :443

# Или через ss
sudo ss -tulpn | grep :8002
sudo ss -tulpn | grep :3002

# Проверка Docker контейнеров
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Должно показать:
# snee-backend    0.0.0.0:8002->8002/tcp
# snee-frontend   0.0.0.0:3002->80/tcp
```

### Тестирование endpoints

```bash
# Backend API
curl http://localhost:8002/api/v1/health
curl https://so-spes.ru/api/v1/health

# Frontend
curl http://localhost:3002
curl https://so-spes.ru

# С сервера
curl http://127.0.0.1:8002/api/v1/health
curl http://127.0.0.1:3002
```

---

## 🔒 Firewall настройки

Если используется UFW (Ubuntu Firewall):

```bash
# Разрешить порты для Docker контейнеров (localhost only)
# Эти порты НЕ должны быть доступны извне напрямую

# Разрешить HTTPS для Nginx
sudo ufw allow 443/tcp

# Разрешить HTTP (для Let's Encrypt)
sudo ufw allow 80/tcp

# Проверка
sudo ufw status
```

**Важно:** Порты 8002 и 3002 должны быть доступны только локально (127.0.0.1), не извне!

---

## 🐛 Решение проблем с портами

### Порт уже занят

```bash
# Найти процесс на порту
sudo lsof -i :8002
sudo lsof -i :3002

# Или
sudo netstat -tulpn | grep :8002

# Убить процесс (замените PID)
sudo kill -9 PID
```

### Docker контейнер не запускается из-за порта

```bash
# Остановить контейнер
docker stop snee-backend

# Проверить, освободился ли порт
sudo lsof -i :8002

# Перезапустить
docker start snee-backend
```

### Nginx не может подключиться к upstream

```bash
# Проверить, что контейнеры запущены
docker ps | grep snee

# Проверить, что порты слушаются
curl http://127.0.0.1:8002/api/v1/health
curl http://127.0.0.1:3002

# Проверить логи Nginx
sudo tail -f /var/log/nginx/snee-graf-error.log

# Перезапустить Nginx
sudo systemctl restart nginx
```

---

## 📝 Изменение портов (если нужно)

Если вы хотите изменить порты, нужно обновить:

### 1. Docker Compose (docker-compose.prod.yml)
```yaml
services:
  snee-backend:
    ports:
      - "НОВЫЙ_ПОРТ:8002"  # Например "9001:8002"
  
  snee-frontend:
    ports:
      - "НОВЫЙ_ПОРТ:80"    # Например "9002:80"
```

### 2. Nginx конфигурация (nginx-server.conf)
```nginx
upstream snee_backend {
    server 127.0.0.1:НОВЫЙ_ПОРТ;  # Например 9001
}

upstream snee_frontend {
    server 127.0.0.1:НОВЫЙ_ПОРТ;  # Например 9002
}
```

### 3. Перезапуск
```bash
# Пересоздать контейнеры
docker-compose down
docker-compose up -d

# Перезапустить Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📚 Дополнительная информация

- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Полная инструкция по развертыванию
- [nginx-server.conf](nginx-server.conf) - Конфигурация Nginx
- [docker-compose.prod.yml](docker-compose.prod.yml) - Docker Compose конфигурация

---

**Текущая конфигурация портов:**
- ✅ Backend: 8002 (локально и продакшен)
- ✅ Frontend: 3002 (локально и продакшен)
- ✅ Домен: so-spes.ru, www.so-spes.ru
- ✅ Docker Hub: end2040/snee_web_spes

