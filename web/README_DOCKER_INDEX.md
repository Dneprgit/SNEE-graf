# 🐳 Docker Deployment - Index

Быстрая навигация по всем Docker файлам и документации.

## 🚀 Быстрый старт

**Хотите запустить прямо сейчас?**

→ **[DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)** ← Начните здесь!

**Время:** 5 минут  
**Команда:** `docker compose up -d`

---

## 📚 Документация

### Для начинающих

1. **[DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)**  
   ⚡ Самый быстрый способ запустить в Docker  
   📊 5 минут от 0 до запущенного приложения

### Для администраторов

2. **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)**  
   📖 Полная инструкция по развертыванию  
   🔒 Production setup с SSL  
   🛠️ Мониторинг, backup, troubleshooting

### Для разработчиков

3. **[DOCKER_FILES_SUMMARY.md](DOCKER_FILES_SUMMARY.md)**  
   📦 Описание всех Docker файлов  
   🏗️ Архитектура и структура  
   🔧 Технические детали

---

## 📁 Docker файлы

### Основные конфигурации

| Файл | Описание | Для кого |
|------|----------|----------|
| **[docker-compose.yml](docker-compose.yml)** | Development/простое развертывание | Разработчики, локальный запуск |
| **[docker-compose.prod.yml](docker-compose.prod.yml)** | Production с SSL и nginx | Администраторы, сервер |
| **[deploy.sh](deploy.sh)** | Автоматический deployment скрипт | Все (самый простой способ) |

### Backend

| Файл | Описание |
|------|----------|
| **[backend/Dockerfile](backend/Dockerfile)** | Docker image для Python backend |
| **[backend/.dockerignore](backend/.dockerignore)** | Исключения при сборке backend |

### Frontend

| Файл | Описание |
|------|----------|
| **[frontend/Dockerfile](frontend/Dockerfile)** | Multi-stage build для React frontend |
| **[frontend/.dockerignore](frontend/.dockerignore)** | Исключения при сборке frontend |
| **[frontend/nginx.conf](frontend/nginx.conf)** | Nginx конфигурация для SPA |

### Nginx Reverse Proxy

| Файл | Описание |
|------|----------|
| **[nginx/nginx.conf](nginx/nginx.conf)** | Production reverse proxy с SSL |

### Environment

| Файл | Описание |
|------|----------|
| **`.env.production.example`** | Пример production environment (создать вручную) |

---

## 🎯 Сценарии использования

### Сценарий 1: Локальная разработка

```bash
cd web
docker compose up -d
```

**Результат:**
- Frontend: http://localhost
- Backend: http://localhost:8002

**Документация:** [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

---

### Сценарий 2: Тестирование на сервере

```bash
cd web
./deploy.sh
# Выбрать "1) Development"
```

**Результат:**
- Автоматическая проверка требований
- Сборка и запуск контейнеров
- Проверка health checks

**Документация:** [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

---

### Сценарий 3: Production развертывание

```bash
cd web

# 1. Подготовка
cp .env.production.example .env.production
nano .env.production

# 2. SSL
mkdir -p nginx/ssl
# Скопировать cert.pem и key.pem

# 3. Запуск
docker compose -f docker-compose.prod.yml up -d
```

**Результат:**
- Frontend: https://your-domain.com
- Backend: https://your-domain.com/api
- SSL termination
- Rate limiting
- Security headers

**Документация:** [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

### Сценарий 4: Автоматический production deploy

```bash
cd web
./deploy.sh
# Выбрать "2) Production"
# Следовать инструкциям
```

**Результат:**
- Интерактивная настройка
- Создание SSL (если нужно)
- Проверка конфигурации
- Автоматический запуск

**Документация:** [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

## 🔍 Быстрый поиск

### Ищете как...

| Задача | Документ | Раздел |
|--------|----------|--------|
| **Запустить быстро** | [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) | "Самый быстрый способ" |
| **Настроить SSL** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Конфигурация → SSL сертификаты" |
| **Настроить домен** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Конфигурация → Environment" |
| **Обновить приложение** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Обслуживание → Обновление" |
| **Сделать backup** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Обслуживание → Backup" |
| **Посмотреть логи** | [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) | "Управление → Просмотр логов" |
| **Решить проблему** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Troubleshooting" |
| **Понять архитектуру** | [DOCKER_FILES_SUMMARY.md](DOCKER_FILES_SUMMARY.md) | "Архитектура Docker" |
| **Настроить CORS** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Конфигурация → Настройка CORS" |
| **Настроить firewall** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | "Безопасность → Firewall" |

---

## ⚙️ Основные команды

### Development

```bash
# Запуск
docker compose up -d

# Статус
docker compose ps

# Логи
docker compose logs -f

# Остановка
docker compose down
```

### Production

```bash
# Запуск
docker compose -f docker-compose.prod.yml up -d

# Статус
docker compose -f docker-compose.prod.yml ps

# Логи
docker compose -f docker-compose.prod.yml logs -f

# Остановка
docker compose -f docker-compose.prod.yml down
```

### Health Checks

```bash
# Backend
curl http://localhost:8002/api/v1/health

# Frontend
curl http://localhost/health

# С SSL
curl https://localhost/health
```

---

## 📊 Архитектура

### Development

```
Browser (:80) → Frontend Container → Backend Container (:8002)
```

### Production

```
Browser (:443 HTTPS)
    ↓
Nginx Proxy (SSL termination, Rate limiting)
    ↓
Frontend Container + Backend Container
```

---

## 🎓 Обучение

### Новичок в Docker?

1. Прочитайте [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
2. Запустите локально: `docker compose up -d`
3. Изучите логи: `docker compose logs -f`
4. Остановите: `docker compose down`

### Опытный пользователь?

1. Изучите [docker-compose.prod.yml](docker-compose.prod.yml)
2. Посмотрите [nginx/nginx.conf](nginx/nginx.conf)
3. Прочитайте [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) → "Безопасность"

### Системный администратор?

1. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - полная инструкция
2. [DOCKER_FILES_SUMMARY.md](DOCKER_FILES_SUMMARY.md) - техническая документация
3. Настройте мониторинг (раздел "Мониторинг")
4. Настройте backup (раздел "Обслуживание → Backup")

---

## ✅ Чеклист развертывания

### Development (локально)

- [ ] Docker установлен
- [ ] Выполнено: `docker compose up -d`
- [ ] Frontend открывается: http://localhost
- [ ] Backend отвечает: http://localhost:8002/api/v1/health

### Production (сервер)

- [ ] Сервер подготовлен (firewall, Docker)
- [ ] DNS настроен (домен указывает на сервер)
- [ ] SSL сертификаты получены и скопированы
- [ ] `.env.production` создан и заполнен
- [ ] Выполнено: `docker compose -f docker-compose.prod.yml up -d`
- [ ] Health checks проходят
- [ ] HTTPS работает
- [ ] Настроен backup
- [ ] Настроен мониторинг

---

## 🔗 Связанная документация

### О приложении

- **[README_SCIPY_FIX.md](README_SCIPY_FIX.md)** - Исправление расчетов scipy
- **[SCIPY_SOLUTION_SUMMARY.md](SCIPY_SOLUTION_SUMMARY.md)** - Детали решения
- **[PPW_VARIANT_README.md](PPW_VARIANT_README.md)** - PPW вариант

### Другие инструкции

- **[API_EXAMPLES.md](API_EXAMPLES.md)** - Примеры API запросов
- **[TESTING.md](TESTING.md)** - Тестирование приложения
- **[USER_GUIDE.md](USER_GUIDE.md)** - Руководство пользователя

---

## 💡 Советы

### Для разработки

- Используйте `docker-compose.yml` (простой)
- Логи в реальном времени: `docker compose logs -f`
- Перезапуск после изменений: `docker compose restart`

### Для продакшн

- Используйте `docker-compose.prod.yml`
- Обязательно настройте SSL (Let's Encrypt)
- Настройте автоматический backup
- Мониторьте health checks
- Обновляйте образы регулярно

### Для безопасности

- Не коммитьте `.env.production`
- Не коммитьте SSL сертификаты
- Используйте сильные пароли
- Настройте firewall
- Обновляйте систему регулярно

---

## 🆘 Нужна помощь?

### Что-то не работает?

1. **Проверьте логи**: `docker compose logs -f`
2. **Проверьте статус**: `docker compose ps`
3. **Смотрите Troubleshooting**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

### Часто задаваемые вопросы

**Q: Порт занят?**  
A: Остановите конфликтующий процесс или измените порт в docker-compose.yml

**Q: SSL не работает?**  
A: Проверьте сертификаты в `nginx/ssl/` и настройки в `.env.production`

**Q: Backend не отвечает?**  
A: `docker compose logs backend` для диагностики

**Q: CORS ошибки?**  
A: Проверьте `CORS_ORIGINS` в `.env.production`

---

## 📞 Контакты

- **Issues**: Создайте issue в репозитории
- **Документация**: Этот файл и связанные документы
- **Примеры**: [API_EXAMPLES.md](API_EXAMPLES.md)

---

**🎉 Готово! Выберите сценарий и начинайте!**

*Обновлено: 2025-12-12*

