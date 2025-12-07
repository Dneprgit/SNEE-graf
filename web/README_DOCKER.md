# 🐳 Docker - Полное руководство для SNЭЭ Graf

**Все о Docker развертывании проекта SNЭЭ Graf на продакшен сервере**

---

## 📚 Содержание документации

Документация разделена на несколько файлов для удобства:

### 1. **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** 📖
Самая подробная инструкция по развертыванию проекта через Docker Hub.

**Что внутри:**
- ✅ Пошаговая инструкция от начала до конца
- ✅ Сборка и push образов в Docker Hub
- ✅ Настройка сервера и развертывание
- ✅ Настройка Nginx с SSL
- ✅ Автозапуск и мониторинг
- ✅ Решение проблем
- ✅ Чек-лист развертывания

**Когда использовать:** Первое развертывание или детальное изучение процесса.

---

### 2. **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)** ⚡
Краткая инструкция для быстрого деплоя.

**Что внутри:**
- ⚡ Только необходимые команды
- ⚡ Минимальная конфигурация
- ⚡ Быстрое обновление

**Когда использовать:** Когда вы уже знаете процесс и нужна быстрая шпаргалка.

---

### 3. **[COMMANDS.md](COMMANDS.md)** 📝
Полная шпаргалка по всем командам Docker, Nginx, SSL.

**Что внутри:**
- 📝 Команды Docker и Docker Compose
- 📝 Команды Nginx
- 📝 Команды SSL (Let's Encrypt)
- 📝 Мониторинг и диагностика
- 📝 Полезные скрипты

**Когда использовать:** Для быстрого поиска нужной команды.

---

## 🚀 Быстрая навигация

### Хочу развернуть проект первый раз
→ Читайте **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)**

### Уже развернул, нужно обновить
→ Смотрите секцию "Обновление проекта" в **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)**  
→ Или быстрая версия в **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)**

### Нужна конкретная команда
→ Ищите в **[COMMANDS.md](COMMANDS.md)**

### Что-то сломалось
→ Секция "Решение проблем" в **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)**  
→ Раздел "Диагностика" в **[COMMANDS.md](COMMANDS.md)**

---

## 📦 Файлы проекта для Docker

### Production Dockerfiles

1. **Dockerfile.backend.prod** - Production образ для FastAPI backend
2. **Dockerfile.frontend.prod** - Multi-stage образ для React frontend

### Docker Compose

1. **docker-compose.yml** - Development конфигурация (с hot-reload)
2. **docker-compose.prod.yml** - Production конфигурация (для сервера)

### Конфигурации

1. **.dockerignore** - Исключения для Docker build
2. **nginx-server.conf** - Готовая конфигурация Nginx для сервера
3. **env.example.prod** - Примеры переменных окружения для продакшена

---

## 🏗️ Архитектура развертывания

```
┌─────────────────────────────────────────────────┐
│         Server: 194.67.84.241 (Reg.ru)         │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │         Nginx             │
        │  (SSL Termination)        │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌───────────────┐
│  CompanyKD    │          │  SNEE Graf    │
│  Container    │          │  Project      │
│  Port: 5000   │          │               │
└───────────────┘          └───────┬───────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
            ┌─────────────────┐        ┌─────────────────┐
            │  snee-backend   │        │  snee-frontend  │
            │  FastAPI        │        │  React + Nginx  │
            │  Port: 8001     │        │  Port: 3001     │
            └─────────────────┘        └─────────────────┘
```

### Потоки данных:

1. **HTTPS → Nginx (443)** - SSL терминация
2. **Nginx → Frontend (3001)** - Статические файлы React
3. **Nginx → Backend (8001)** - API запросы
4. **Frontend → Backend** - Запросы через Nginx proxy

---

## 🔧 Workflow развертывания

### 1. Разработка (локально)
```
Code Changes → Git Commit
```

### 2. Сборка образов (локально, Windows)
```
Source Code → Docker Build → Docker Images
```

### 3. Публикация (Docker Hub)
```
Docker Images → Docker Push → Docker Hub
```

### 4. Развертывание (сервер)
```
Docker Hub → Docker Pull → Server → Docker Compose Up
```

### 5. Обновление
```
New Version → Repeat steps 2-4
```

---

## 🔐 Безопасность

### SSL/TLS
- ✅ Let's Encrypt SSL сертификаты
- ✅ Автоматическое обновление (certbot)
- ✅ Редирект HTTP → HTTPS
- ✅ Modern TLS настройки (TLS 1.2+)

### Docker
- ✅ Изолированная сеть (bridge network)
- ✅ Health checks для контейнеров
- ✅ Restart policy (always)
- ✅ Минимальные образы (slim, alpine)

### Nginx
- ✅ Security headers (HSTS, XSS Protection, etc.)
- ✅ Rate limiting (можно настроить)
- ✅ Client max body size (10MB)
- ✅ Proxy timeouts

---

## 📊 Мониторинг

### Логи контейнеров
```bash
docker-compose logs -f
```

### Логи Nginx
```bash
sudo tail -f /var/log/nginx/snee-graf-access.log
sudo tail -f /var/log/nginx/snee-graf-error.log
```

### Использование ресурсов
```bash
docker stats
htop
df -h
```

### Health Checks
```bash
# API
curl https://snee.companykd.world/api/v1/health

# Frontend
curl https://snee.companykd.world
```

---

## 🔄 CI/CD (будущее)

Рекомендации для настройки CI/CD:

### GitHub Actions пример:
```yaml
name: Deploy SNEE Graf

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker images
        run: |
          docker build -f web/Dockerfile.backend.prod -t ${{ secrets.DOCKER_USERNAME }}/snee-backend:latest .
          docker build -f web/Dockerfile.frontend.prod -t ${{ secrets.DOCKER_USERNAME }}/snee-frontend:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/snee-backend:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/snee-frontend:latest
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/snee-graf
            docker-compose pull
            docker-compose up -d --force-recreate
```

---

## 🆘 Поддержка

### Документация
1. [Docker Documentation](https://docs.docker.com/)
2. [Nginx Documentation](https://nginx.org/en/docs/)
3. [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

### Логи и диагностика
```bash
# Запустите скрипт проверки
/opt/snee-graf/check-status.sh

# Смотрите логи
docker-compose logs -f
```

### Контакты
- 📧 Email: support@example.com
- 🐛 GitHub Issues: [ссылка на репозиторий]

---

## ✅ Чек-лист готовности к продакшену

### Перед развертыванием
- [ ] Код протестирован локально
- [ ] Переменные окружения настроены
- [ ] Docker Hub репозитории созданы
- [ ] DNS записи настроены (если нужен поддомен)
- [ ] Доступ по SSH к серверу получен

### После развертывания
- [ ] Контейнеры запущены и здоровы
- [ ] API отвечает на health check
- [ ] Frontend открывается в браузере
- [ ] SSL сертификат установлен и работает
- [ ] Все функции приложения протестированы
- [ ] Мониторинг настроен
- [ ] Backup конфигураций создан

---

## 🎓 Полезные ресурсы

### Обучающие материалы
- [Docker для начинающих](https://docs.docker.com/get-started/)
- [Docker Compose руководство](https://docs.docker.com/compose/)
- [Nginx для начинающих](https://nginx.org/en/docs/beginners_guide.html)

### Инструменты
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Docker Hub](https://hub.docker.com/)
- [Portainer](https://www.portainer.io/) - GUI для Docker

---

## 📈 Версионирование образов

### Стратегия тегирования:
```bash
# Latest - текущая версия
your_username/snee-backend:latest

# Версия - семантическое версионирование
your_username/snee-backend:v1.0.0
your_username/snee-backend:v1.1.0
your_username/snee-backend:v2.0.0

# Git commit hash
your_username/snee-backend:abc123
```

### Пример использования версий:
```bash
# Сборка с версией
docker build -t username/snee-backend:v1.0.0 .
docker build -t username/snee-backend:latest .

# Push обеих тегов
docker push username/snee-backend:v1.0.0
docker push username/snee-backend:latest
```

---

## 🎉 Заключение

Эта документация охватывает весь процесс развертывания проекта SNЭЭ Graf через Docker.

**Начните с:**
1. Прочитайте [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
2. Используйте [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) для быстрых задач
3. Держите [COMMANDS.md](COMMANDS.md) под рукой

**Удачи в развертывании! 🚀**

