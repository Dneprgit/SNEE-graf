# 🐳 Docker Deployment Guide - SNEE Graf

Полная инструкция по развертыванию SNEE Graf в Docker на продакшн сервере.

## 📋 Содержание

- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Структура файлов](#структура-файлов)
- [Конфигурация](#конфигурация)
- [Развертывание](#развертывание)
- [Мониторинг](#мониторинг)
- [Обслуживание](#обслуживание)
- [Безопасность](#безопасность)

---

## 🔧 Требования

### Минимальные требования сервера

- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 20 GB
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Проверка
docker --version
docker compose version
```

---

## 🚀 Быстрый старт

### Вариант 1: Простое развертывание (без SSL)

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd web

# 2. Запустить с docker-compose
docker compose up -d

# 3. Проверить статус
docker compose ps

# 4. Открыть в браузере
# Frontend: http://localhost
# Backend API: http://localhost:8002
```

### Вариант 2: Production развертывание (с SSL и nginx)

```bash
# 1. Подготовить environment
cp .env.production.example .env.production
nano .env.production  # Заполнить переменные

# 2. Подготовить SSL сертификаты
mkdir -p nginx/ssl
# Скопировать cert.pem и key.pem в nginx/ssl/

# 3. Запустить production стек
docker compose -f docker-compose.prod.yml up -d

# 4. Проверить логи
docker compose -f docker-compose.prod.yml logs -f
```

---

## 📁 Структура файлов

```
web/
├── backend/
│   ├── Dockerfile              # Backend Docker image
│   ├── .dockerignore          # Исключения для backend
│   ├── requirements.txt       # Python зависимости
│   └── main.py                # Точка входа
│
├── frontend/
│   ├── Dockerfile             # Frontend Docker image (multi-stage)
│   ├── .dockerignore         # Исключения для frontend
│   ├── nginx.conf            # Nginx конфигурация для SPA
│   └── package.json          # Node.js зависимости
│
├── nginx/
│   ├── nginx.conf            # Production reverse proxy config
│   └── ssl/                  # SSL сертификаты
│       ├── cert.pem
│       └── key.pem
│
├── docker-compose.yml         # Базовая конфигурация
├── docker-compose.prod.yml    # Production конфигурация
├── .env.production.example    # Пример environment файла
│
├── data/                      # Персистентные данные (создается автоматически)
└── logs/                      # Логи (создается автоматически)
    ├── backend/
    └── nginx/
```

---

## ⚙️ Конфигурация

### 1. Environment переменные

Создайте `.env.production`:

```bash
# API Configuration
API_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# Backend
API_HOST=0.0.0.0
API_PORT=8002
LOG_LEVEL=WARNING

# Frontend
VITE_API_URL=https://your-domain.com
```

### 2. SSL сертификаты

**Вариант A: Let's Encrypt (рекомендуется)**

```bash
# Установка certbot
sudo apt-get install certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Копирование в проект
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*.pem
```

**Вариант B: Self-signed (для тестирования)**

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

### 3. Настройка CORS

В `.env.production` укажите разрешенные origins:

```bash
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

---

## 🚀 Развертывание

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y git curl wget

# Настройка firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Шаг 2: Клонирование проекта

```bash
# Клонирование
git clone <repository-url> snee-graf
cd snee-graf/web

# Права доступа
chmod +x *.sh  # Если есть скрипты
```

### Шаг 3: Конфигурация

```bash
# Environment
cp .env.production.example .env.production
nano .env.production

# SSL (если нужно)
mkdir -p nginx/ssl
# Скопировать сертификаты
```

### Шаг 4: Build и запуск

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Запуск в detached режиме
docker compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker compose -f docker-compose.prod.yml ps
```

### Шаг 5: Проверка работоспособности

```bash
# Health checks
curl http://localhost/health         # Frontend
curl http://localhost:8002/api/v1/health  # Backend

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

---

## 📊 Мониторинг

### Health Checks

Все сервисы имеют встроенные health checks:

```bash
# Проверка через Docker
docker ps  # Смотреть колонку STATUS

# Backend health
curl http://localhost:8002/api/v1/health
# Ожидается: {"status":"healthy","service":"SNEE Graf API"}

# Frontend health
curl http://localhost/health
# Ожидается: healthy
```

### Просмотр логов

```bash
# Все логи
docker compose -f docker-compose.prod.yml logs

# Конкретный сервис
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs nginx

# Follow режим (реального времени)
docker compose -f docker-compose.prod.yml logs -f --tail=100

# Сохранить логи в файл
docker compose -f docker-compose.prod.yml logs > logs.txt
```

### Использование ресурсов

```bash
# Статистика контейнеров
docker stats

# Использование диска
docker system df

# Детальная информация
docker compose -f docker-compose.prod.yml ps -a
```

---

## 🔄 Обслуживание

### Обновление приложения

```bash
# 1. Получить обновления
git pull origin main

# 2. Rebuild images
docker compose -f docker-compose.prod.yml build

# 3. Recreate контейнеры (zero-downtime)
docker compose -f docker-compose.prod.yml up -d --no-deps --build backend
docker compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# 4. Проверить
docker compose -f docker-compose.prod.yml ps
```

### Backup данных

```bash
# Backup данных
tar -czf backup-data-$(date +%Y%m%d).tar.gz data/

# Backup базы данных (если используется)
docker compose -f docker-compose.prod.yml exec backend \
  python -c "from data_manager import DataManager; DataManager.export_all()"

# Копирование на удаленный сервер
scp backup-*.tar.gz user@backup-server:/backups/
```

### Restore данных

```bash
# Остановить сервисы
docker compose -f docker-compose.prod.yml down

# Восстановить данные
tar -xzf backup-data-YYYYMMDD.tar.gz

# Запустить сервисы
docker compose -f docker-compose.prod.yml up -d
```

### Очистка

```bash
# Остановка и удаление контейнеров
docker compose -f docker-compose.prod.yml down

# Удаление неиспользуемых images
docker image prune -a

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

---

## 🔒 Безопасность

### 1. SSL/TLS

- ✅ Используйте Let's Encrypt для бесплатных SSL сертификатов
- ✅ Обновляйте сертификаты каждые 90 дней
- ✅ Настройте автообновление через cron

```bash
# Cron для автообновления (Let's Encrypt)
0 0 1 * * certbot renew --quiet && docker compose -f /path/to/docker-compose.prod.yml restart nginx
```

### 2. Firewall

```bash
# UFW конфигурация
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Docker Security

```bash
# Запуск с непривилегированным пользователем (уже настроено в Dockerfile)
# Ограничение ресурсов (настроено в docker-compose.prod.yml)

# Проверка безопасности images
docker scan snee-graf-backend
docker scan snee-graf-frontend
```

### 4. Регулярные обновления

```bash
# Обновление базовых images
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Обновление системных пакетов
sudo apt update && sudo apt upgrade -y
```

### 5. Rate Limiting

Настроено в `nginx/nginx.conf`:
- API: 10 requests/second
- General: 30 requests/second

### 6. Секреты

**НЕ КОММИТЬТЕ:**
- `.env.production`
- SSL сертификаты
- Любые пароли/токены

Используйте `.gitignore`:
```
.env.production
nginx/ssl/*.pem
*.key
*.crt
```

---

## 🐛 Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Просмотр логов
docker compose -f docker-compose.prod.yml logs backend

# Проверка конфигурации
docker compose -f docker-compose.prod.yml config

# Запуск в foreground режиме
docker compose -f docker-compose.prod.yml up
```

### Проблема: Backend недоступен

```bash
# Проверка портов
sudo netstat -tulpn | grep 8002

# Проверка health check
docker inspect snee-graf-backend | grep -A 10 Health

# Перезапуск
docker compose -f docker-compose.prod.yml restart backend
```

### Проблема: CORS ошибки

```bash
# Проверить CORS_ORIGINS в .env.production
cat .env.production | grep CORS

# Обновить и перезапустить
docker compose -f docker-compose.prod.yml up -d --force-recreate backend
```

### Проблема: Недостаточно памяти

```bash
# Увеличить лимиты в docker-compose.prod.yml
# resources:
#   limits:
#     memory: 4G

# Перезапустить с новыми лимитами
docker compose -f docker-compose.prod.yml up -d
```

---

## 📝 Полезные команды

```bash
# Статус сервисов
docker compose -f docker-compose.prod.yml ps

# Логи
docker compose -f docker-compose.prod.yml logs -f

# Перезапуск
docker compose -f docker-compose.prod.yml restart

# Остановка
docker compose -f docker-compose.prod.yml stop

# Запуск
docker compose -f docker-compose.prod.yml start

# Полное удаление
docker compose -f docker-compose.prod.yml down -v

# Exec в контейнер
docker compose -f docker-compose.prod.yml exec backend bash
docker compose -f docker-compose.prod.yml exec frontend sh

# Просмотр использования ресурсов
docker stats

# Очистка логов
truncate -s 0 logs/backend/*.log
truncate -s 0 logs/nginx/*.log
```

---

## 🎯 Best Practices

1. **Мониторинг**: Настройте external мониторинг (UptimeRobot, Pingdom)
2. **Backup**: Автоматизируйте backup через cron
3. **Логи**: Используйте log rotation для предотвращения переполнения диска
4. **Updates**: Регулярно обновляйте images и систему
5. **Security**: Подпишитесь на security advisories для используемых технологий

---

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://reactjs.org/docs/optimizing-performance.html)

---

**Вопросы?** Проверьте [README_SCIPY_FIX.md](README_SCIPY_FIX.md) для информации о приложении.

*Последнее обновление: 2025-12-12*
