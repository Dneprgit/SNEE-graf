# 🔌 Информация о портах SNЭЭ Graf

## 📊 Схема портов

### Локальная разработка (без Docker)
```
Backend:   http://localhost:8001
Frontend:  http://localhost:3001
```

### Production на сервере Reg.ru (194.67.84.241)
```
Backend:   http://194.67.84.241:8001
Frontend:  http://194.67.84.241:3001

Через домен (с Nginx + SSL):
https://snee.companykd.world
```

### Другие проекты на том же сервере
```
CompanyKD: http://194.67.84.241:5000
           https://companykd.world
```

---

## 🐳 Docker контейнеры

### Внутренние порты контейнеров
```
snee-backend:   порт 8001 внутри контейнера
snee-frontend:  порт 80 внутри контейнера (Nginx)
```

### Проброс портов (host:container)
```
Backend:   8001:8001
Frontend:  3001:80
```

**Команда в docker-compose.prod.yml:**
```yaml
services:
  snee-backend:
    ports:
      - "8001:8001"
  
  snee-frontend:
    ports:
      - "3001:80"
```

---

## 🌐 Nginx конфигурация

### Upstreams
```nginx
upstream snee_backend {
    server 127.0.0.1:8001;
}

upstream snee_frontend {
    server 127.0.0.1:3001;
}
```

### Locations
```nginx
server {
    listen 443 ssl http2;
    server_name snee.companykd.world;
    
    # Frontend
    location / {
        proxy_pass http://snee_frontend;  # → 127.0.0.1:3001
    }
    
    # Backend API
    location /api {
        proxy_pass http://snee_backend;    # → 127.0.0.1:8001
    }
}
```

---

## 🔄 Поток запросов

### Пользователь → Приложение

```
1. Пользователь открывает:
   https://snee.companykd.world

2. Nginx получает запрос на порту 443 (HTTPS)

3. Nginx проксирует на frontend контейнер:
   127.0.0.1:3001 (Docker порт snee-frontend)

4. Frontend отдает React приложение

5. React приложение делает API запросы:
   https://snee.companykd.world/api/v1/...

6. Nginx проксирует API запросы на backend:
   127.0.0.1:8001 (Docker порт snee-backend)

7. Backend обрабатывает и возвращает результат
```

### Схема
```
Браузер
   ↓ HTTPS (443)
Nginx (SSL терминация)
   ↓
   ├─→ / (frontend) → 127.0.0.1:3001 → Docker snee-frontend
   └─→ /api         → 127.0.0.1:8001 → Docker snee-backend
```

---

## ✅ Проверка портов

### На сервере

```bash
# Проверка, что порты слушаются
sudo netstat -tulpn | grep :8001
sudo netstat -tulpn | grep :3001
sudo netstat -tulpn | grep :443

# Или через ss
sudo ss -tulpn | grep :8001
sudo ss -tulpn | grep :3001

# Проверка Docker контейнеров
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Должно показать:
# snee-backend    0.0.0.0:8001->8001/tcp
# snee-frontend   0.0.0.0:3001->80/tcp
```

### Тестирование endpoints

```bash
# Backend API
curl http://localhost:8001/api/v1/health
curl https://snee.companykd.world/api/v1/health

# Frontend
curl http://localhost:3001
curl https://snee.companykd.world

# С сервера
curl http://127.0.0.1:8001/api/v1/health
curl http://127.0.0.1:3001
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

**Важно:** Порты 8001 и 3001 должны быть доступны только локально (127.0.0.1), не извне!

---

## 🐛 Решение проблем с портами

### Порт уже занят

```bash
# Найти процесс на порту
sudo lsof -i :8001
sudo lsof -i :3001

# Или
sudo netstat -tulpn | grep :8001

# Убить процесс (замените PID)
sudo kill -9 PID
```

### Docker контейнер не запускается из-за порта

```bash
# Остановить контейнер
docker stop snee-backend

# Проверить, освободился ли порт
sudo lsof -i :8001

# Перезапустить
docker start snee-backend
```

### Nginx не может подключиться к upstream

```bash
# Проверить, что контейнеры запущены
docker ps | grep snee

# Проверить, что порты слушаются
curl http://127.0.0.1:8001/api/v1/health
curl http://127.0.0.1:3001

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
      - "НОВЫЙ_ПОРТ:8001"  # Например "9001:8001"
  
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
- ✅ Backend: 8001 (локально и продакшен)
- ✅ Frontend: 3001 (локально и продакшен)
- ✅ CompanyKD: 5000 (продакшен, существующий проект)

