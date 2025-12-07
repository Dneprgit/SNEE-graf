# 📦 Обзор файлов для Docker развертывания

**Все файлы, созданные для развертывания SNЭЭ Graf через Docker**

---

## 📋 Быстрая навигация

| Тип | Файл | Описание |
|-----|------|----------|
| 📖 | [README_DOCKER.md](README_DOCKER.md) | Главный обзор Docker развертывания |
| 📘 | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Полная пошаговая инструкция |
| ⚡ | [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) | Быстрый старт |
| 📝 | [COMMANDS.md](COMMANDS.md) | Шпаргалка по командам |
| 🐳 | [Dockerfile.backend.prod](Dockerfile.backend.prod) | Production образ backend |
| 🐳 | [Dockerfile.frontend.prod](Dockerfile.frontend.prod) | Production образ frontend |
| 🔧 | [docker-compose.prod.yml](docker-compose.prod.yml) | Production конфигурация |
| 🌐 | [nginx-server.conf](nginx-server.conf) | Nginx конфигурация для сервера |
| 🚫 | [.dockerignore](.dockerignore) | Исключения для Docker build |
| 📄 | [backend/env.example.prod](backend/env.example.prod) | Пример переменных backend |
| 📄 | [frontend/env.example.prod](frontend/env.example.prod) | Пример переменных frontend |

### Скрипты автоматизации (scripts/)

| Скрипт | Назначение |
|--------|------------|
| [install-server.sh](scripts/install-server.sh) | Первоначальная установка |
| [check-status.sh](scripts/check-status.sh) | Проверка статуса |
| [update.sh](scripts/update.sh) | Обновление проекта |
| [restart.sh](scripts/restart.sh) | Перезапуск сервисов |
| [logs.sh](scripts/logs.sh) | Просмотр логов |
| [README.md](scripts/README.md) | Документация скриптов |

---

## 🎯 С чего начать?

### 1️⃣ Для первого развертывания

Начните с чтения **[README_DOCKER.md](README_DOCKER.md)** - там есть навигация по всем документам.

Затем следуйте **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - там пошаговая инструкция.

### 2️⃣ Если уже знакомы с процессом

Используйте **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)** для быстрого деплоя.

### 3️⃣ Для поиска команд

Открывайте **[COMMANDS.md](COMMANDS.md)** - там все команды с примерами.

---

## 📁 Детальное описание файлов

### 📖 Документация

#### README_DOCKER.md
**Главный файл** с обзором всего процесса Docker развертывания.

**Содержит:**
- Навигацию по всем документам
- Архитектуру развертывания
- Workflow процесса
- Безопасность и мониторинг

**Когда читать:** Первым делом для понимания общей картины.

---

#### DOCKER_DEPLOYMENT.md
**Самая подробная инструкция** - 800+ строк пошаговых действий.

**Содержит:**
- 7 больших частей от подготовки до мониторинга
- Скриншоты команд с ожидаемым выводом
- Решение типичных проблем
- Чек-лист развертывания

**Когда читать:** При первом развертывании или когда нужны детали.

---

#### QUICKSTART_DOCKER.md
**Краткая версия** для быстрого деплоя.

**Содержит:**
- Только необходимые команды
- Минимальные конфигурации
- Быстрое обновление

**Когда читать:** Когда уже знаете процесс и нужна шпаргалка.

---

#### COMMANDS.md
**Справочник команд** - все команды Docker, Nginx, SSL.

**Содержит:**
- Команды Docker и Docker Compose
- Команды Nginx
- SSL сертификаты (Let's Encrypt)
- Мониторинг и диагностика
- Резервное копирование
- Полезные скрипты

**Когда читать:** Для быстрого поиска нужной команды.

---

### 🐳 Docker файлы

#### Dockerfile.backend.prod
Production Dockerfile для FastAPI backend.

**Особенности:**
- Базовый образ: `python:3.11-slim`
- Копирует родительские модули для импорта
- Устанавливает зависимости из requirements.txt
- Запускает Uvicorn с 2 workers
- Порт: 8001

**Размер образа:** ~200MB

---

#### Dockerfile.frontend.prod
Multi-stage Production Dockerfile для React frontend.

**Stage 1 - Builder:**
- Базовый образ: `node:18-alpine`
- Собирает production build (`npm run build`)

**Stage 2 - Runtime:**
- Базовый образ: `nginx:alpine`
- Копирует собранные файлы
- Настраивает Nginx для SPA
- Порт: 80

**Размер образа:** ~50MB

---

#### docker-compose.prod.yml
Production конфигурация Docker Compose.

**Сервисы:**
- `snee-backend` - FastAPI API (порт 8001)
- `snee-frontend` - React + Nginx (порт 3001)

**Настройки:**
- `restart: always` - автоперезапуск
- Health checks для мониторинга
- Изолированная сеть `snee-network`

---

#### .dockerignore
Исключения для Docker build.

**Исключает:**
- `node_modules/`, `venv/`
- `__pycache__/`, `*.pyc`
- `.git/`, `.env`
- Логи, временные файлы
- Документацию (кроме README)

**Эффект:** Уменьшает размер контекста сборки и образа.

---

### 🌐 Nginx конфигурация

#### nginx-server.conf
Готовая production конфигурация Nginx для сервера.

**Настроено:**
- ✅ HTTP → HTTPS редирект
- ✅ SSL/TLS (Let's Encrypt)
- ✅ Security headers (HSTS, XSS Protection)
- ✅ Gzip сжатие
- ✅ Proxy для backend API
- ✅ Proxy для frontend
- ✅ Таймауты и лимиты

**Upstreams:**
- `snee_backend` → 127.0.0.1:8001
- `snee_frontend` → 127.0.0.1:3001

**Locations:**
- `/api` → проксирует на backend
- `/docs`, `/redoc`, `/openapi.json` → API документация
- `/` → проксирует на frontend

---

### 📄 Переменные окружения

#### backend/env.example.prod
Пример переменных окружения для production backend.

**Переменные:**
```env
ENVIRONMENT=production
API_TITLE=SNEE Graf API
ALLOWED_ORIGINS=https://snee.companykd.world
MAX_UPLOAD_SIZE=10485760
LOG_LEVEL=INFO
WORKERS=2
```

---

#### frontend/env.example.prod
Пример переменных окружения для production frontend.

**Переменные:**
```env
VITE_API_URL=https://snee.companykd.world/api
VITE_APP_TITLE=СНЭЭ Graf
VITE_MODE=production
```

---

### 🛠️ Скрипты автоматизации

#### scripts/install-server.sh
Автоматическая установка проекта на чистый сервер.

**Что делает:**
1. Обновляет систему
2. Устанавливает Docker и Docker Compose
3. Создает директории
4. Создает docker-compose.yml
5. Загружает и запускает контейнеры
6. Проверяет работоспособность

**Использование:**
```bash
sudo ./install-server.sh
```

---

#### scripts/check-status.sh
Комплексная проверка статуса всех компонентов.

**Проверяет:**
- Docker и контейнеры
- Health checks
- API endpoints
- Nginx
- Использование ресурсов
- SSL сертификаты
- Ошибки в логах

**Использование:**
```bash
./check-status.sh
```

---

#### scripts/update.sh
Безопасное обновление проекта до новой версии.

**Что делает:**
1. Создает backup
2. Скачивает новые образы
3. Пересоздает контейнеры
4. Проверяет работоспособность
5. Удаляет старые образы

**Использование:**
```bash
./update.sh
```

---

#### scripts/restart.sh
Перезапуск сервисов.

**Использование:**
```bash
./restart.sh [backend|frontend|all]
```

---

#### scripts/logs.sh
Просмотр логов.

**Использование:**
```bash
./logs.sh [backend|frontend|nginx|all]
```

---

## 🚀 Типичный workflow

### Первое развертывание

```bash
# 1. Локально: Сборка образов
cd web
docker build -f Dockerfile.backend.prod -t username/snee-backend:latest ..
docker build -f Dockerfile.frontend.prod -t username/snee-frontend:latest ..

# 2. Push в Docker Hub
docker push username/snee-backend:latest
docker push username/snee-frontend:latest

# 3. На сервере: Установка
sudo ./scripts/install-server.sh

# 4. Настройка Nginx
sudo nano /etc/nginx/sites-available/snee-graf
# (копируем nginx-server.conf)

# 5. SSL сертификат
sudo certbot --nginx -d snee.companykd.world

# 6. Проверка
./scripts/check-status.sh
```

### Обновление

```bash
# 1. Локально: Пересборка
docker build -f Dockerfile.backend.prod -t username/snee-backend:latest ..
docker push username/snee-backend:latest

# 2. На сервере: Обновление
./scripts/update.sh
```

---

## 📊 Архитектура

```
Internet
    ↓
Nginx (443) + SSL
    ↓
    ├─→ /api → Backend Container (8001)
    └─→ /    → Frontend Container (3001)
```

---

## ✅ Чек-лист файлов

Перед развертыванием убедитесь, что у вас есть:

**Docker файлы:**
- [ ] Dockerfile.backend.prod
- [ ] Dockerfile.frontend.prod
- [ ] docker-compose.prod.yml
- [ ] .dockerignore

**Конфигурации:**
- [ ] nginx-server.conf
- [ ] backend/env.example.prod
- [ ] frontend/env.example.prod

**Документация:**
- [ ] README_DOCKER.md
- [ ] DOCKER_DEPLOYMENT.md
- [ ] QUICKSTART_DOCKER.md
- [ ] COMMANDS.md

**Скрипты:**
- [ ] scripts/install-server.sh
- [ ] scripts/check-status.sh
- [ ] scripts/update.sh
- [ ] scripts/restart.sh
- [ ] scripts/logs.sh
- [ ] scripts/README.md

---

## 🎓 Рекомендуемый порядок изучения

1. **[README_DOCKER.md](README_DOCKER.md)** - общая картина
2. **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - детальная инструкция
3. **[scripts/README.md](scripts/README.md)** - скрипты автоматизации
4. **[COMMANDS.md](COMMANDS.md)** - держите под рукой

**Быстрый путь:**
- Если спешите → **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)**

---

## 📞 Поддержка

При проблемах:
1. Проверьте [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) раздел "Решение проблем"
2. Запустите `./scripts/check-status.sh`
3. Изучите логи: `./scripts/logs.sh all`
4. Посмотрите [COMMANDS.md](COMMANDS.md) для диагностики

---

**Создано для проекта SNЭЭ Graf**  
**Версия документации: 1.0**  
**Дата: Декабрь 2024**

