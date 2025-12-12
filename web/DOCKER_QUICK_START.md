# 🐳 Docker Quick Start - SNEE Graf

Быстрая инструкция для запуска в Docker за 5 минут.

## ⚡ Самый быстрый способ (Development)

```bash
# 1. Перейти в директорию web
cd web

# 2. Запустить
docker compose up -d

# 3. Открыть браузер
http://localhost        # Frontend
http://localhost:8002   # Backend API
```

**Готово!** 🎉

---

## 🚀 С помощью скрипта (рекомендуется)

### Linux/Mac

```bash
cd web
./deploy.sh
```

### Windows

```powershell
cd web
docker compose up -d
```

Скрипт автоматически:
- ✅ Проверит Docker и Docker Compose
- ✅ Создаст необходимые директории
- ✅ Соберет images
- ✅ Запустит контейнеры
- ✅ Проверит health checks

---

## 📋 Минимальные требования

- Docker 20.10+
- Docker Compose 2.0+
- 4 GB RAM
- 10 GB свободного места

---

## 🔧 Управление

### Просмотр статуса

```bash
docker compose ps
```

### Просмотр логов

```bash
# Все логи
docker compose logs -f

# Backend
docker compose logs -f backend

# Frontend
docker compose logs -f frontend
```

### Перезапуск

```bash
docker compose restart
```

### Остановка

```bash
docker compose stop
```

### Запуск

```bash
docker compose start
```

### Полная остановка и удаление

```bash
docker compose down
```

---

## 🌐 Production развертывание

Для продакшн сервера с SSL:

```bash
# 1. Подготовить environment
cp .env.production.example .env.production
nano .env.production  # Заполнить

# 2. SSL сертификаты
mkdir -p nginx/ssl
# Скопировать cert.pem и key.pem

# 3. Запустить
docker compose -f docker-compose.prod.yml up -d
```

---

## ❓ Что-то не работает?

### Backend не отвечает

```bash
# Проверить логи
docker compose logs backend

# Перезапустить
docker compose restart backend
```

### Frontend не загружается

```bash
# Проверить логи
docker compose logs frontend

# Проверить nginx
docker compose exec frontend cat /etc/nginx/nginx.conf
```

### Порт занят

```bash
# Проверить какой процесс использует порт
# Linux/Mac:
sudo lsof -i :80
sudo lsof -i :8002

# Windows:
netstat -ano | findstr :80
netstat -ano | findstr :8002

# Остановить конфликтующий контейнер
docker ps
docker stop <container_id>
```

---

## 📚 Дополнительная информация

- **Полная документация**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Production setup**: [docker-compose.prod.yml](docker-compose.prod.yml)
- **Архитектура**: [README_SCIPY_FIX.md](README_SCIPY_FIX.md)

---

## ✅ Проверка работоспособности

После запуска проверьте:

```bash
# Backend health
curl http://localhost:8002/api/v1/health
# Ожидается: {"status":"healthy","service":"SNEE Graf API"}

# Frontend
curl http://localhost/health
# Ожидается: healthy

# API Docs
open http://localhost:8002/docs  # или откройте в браузере
```

---

## 🎯 Структура сервисов

```
┌─────────────────┐
│   Browser       │
│  :80 or :443    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Nginx/Frontend │  ← React SPA
│  Container      │
└────────┬────────┘
         │ API calls
         ▼
┌─────────────────┐
│  Backend        │  ← FastAPI
│  Container      │
│  :8002          │
└─────────────────┘
```

---

**Готово! Приложение запущено в Docker.** 🐳

*Для продакшн развертывания смотрите [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)*

