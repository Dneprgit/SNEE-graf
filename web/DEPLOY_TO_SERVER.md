# 🚀 Развертывание на сервере Reg.ru

**Образы успешно загружены в Docker Hub!**

- ✅ `end2040/snee-backend:latest`
- ✅ `end2040/snee-frontend:latest`

---

## 📋 Следующие шаги

### 1. Подключитесь к серверу

```bash
ssh root@194.67.84.241
```

### 2. Создайте директорию проекта

```bash
sudo mkdir -p /opt/snee-graf
cd /opt/snee-graf
```

### 3. Создайте docker-compose.yml

```bash
nano docker-compose.yml
```

Вставьте содержимое (скопируйте из `docker-compose.server.yml`):

```yaml
version: '3.8'

services:
  snee-backend:
    image: end2040/snee-backend:latest
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
    image: end2040/snee-frontend:latest
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

Сохраните: `Ctrl+X`, `Y`, `Enter`

### 4. Загрузите образы с Docker Hub

```bash
docker-compose pull
```

### 5. Запустите контейнеры

```bash
docker-compose up -d
```

### 6. Проверьте статус

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f

# Проверка API
curl http://localhost:8001/api/v1/health

# Проверка Frontend
curl http://localhost:3001
```

---

## 🌐 Настройка Nginx

### 1. Создайте конфигурацию Nginx

```bash
sudo nano /etc/nginx/sites-available/snee-graf
```

Вставьте содержимое из файла `nginx-server.conf`

### 2. Активируйте конфигурацию

```bash
sudo ln -s /etc/nginx/sites-available/snee-graf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Настройте DNS (если нужен поддомен)

Добавьте A-запись для `snee.companykd.world` → `194.67.84.241`

### 4. Получите SSL сертификат

```bash
sudo certbot --nginx -d snee.companykd.world
```

---

## ✅ Проверка

После всех настроек проверьте:

```bash
# API через Nginx
curl https://snee.companykd.world/api/v1/health

# Frontend через браузер
https://snee.companykd.world
```

---

## 📚 Полная документация

Для детальной информации смотрите:
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - полная пошаговая инструкция
- **[INDEX_DOCKER.md](INDEX_DOCKER.md)** - навигация по документации

---

## 🔄 Обновление проекта

Когда нужно обновить:

### На локальной машине (Windows):
```powershell
# Пересоберите образы
$env:DOCKER_USERNAME = "end2040"
docker build -f Dockerfile.backend.prod -t end2040/snee-backend:latest ..
docker build -f Dockerfile.frontend.prod -t end2040/snee-frontend:latest ..

# Push в Docker Hub
docker push end2040/snee-backend:latest
docker push end2040/snee-frontend:latest
```

### На сервере:
```bash
cd /opt/snee-graf
docker-compose pull
docker-compose up -d --force-recreate
docker image prune -f
```

---

**Готово! Образы в Docker Hub, можно развертывать на сервере! 🎉**


🔄 Полный процесс обновления
Вариант 1: Используя docker-compose (рекомендуется)
# Переходим в директорию проекта
cd /opt/snee-graf

# Останавливаем и удаляем контейнеры
docker-compose down

# Удаляем старые образы
docker rmi end2040/snee-backend:latest
docker rmi end2040/snee-frontend:latest

# Загружаем новые образы из Docker Hub
docker-compose pull

# Запускаем с новыми образами
docker-compose up -d


Вариант 2: Используя обычные команды Docker
# 1. Остановить контейнеры
docker stop snee-backend
docker stop snee-frontend

# 2. Удалить контейнеры
docker rm snee-backend
docker rm snee-frontend

# 3. Удалить образы
docker rmi end2040/snee-backend:latest
docker rmi end2040/snee-frontend:latest

# 4. Загрузить новые образы
docker pull end2040/snee-backend:latest
docker pull end2040/snee-frontend:latest

# 5. Запустить контейнеры снова
cd /opt/snee-graf
docker-compose up -d


🚀 Быстрая команда "всё в одном"
cd /opt/snee-graf && \
docker-compose down && \
docker rmi end2040/snee-backend:latest end2040/snee-frontend:latest && \
docker-compose pull && \
docker-compose up -d


🧹 Дополнительные полезные команды
Посмотреть запущенные контейнеры
docker ps

Посмотреть ВСЕ контейнеры (включая остановленные)
docker ps -a

Посмотреть все образы
docker images

Очистить неиспользуемые образы (освободить место)
# Только неиспользуемые (dangling) образы
docker image prune -f
# ВСЕ неиспользуемые образы (осторожно!)
docker image prune -a -f

Посмотреть логи контейнеров
# Логи в реальном времени
docker-compose logs -f
# Последние 50 строк
docker-compose logs --tail=50
# Логи конкретного сервиса
docker-compose logs -f snee-backend

Проверить статус после запуска
# Статус контейнеров
docker-compose ps
# Health check API
curl http://localhost:8001/api/v1/health
# Health check Frontend
curl http://localhost:3001


📝 Рекомендуемая последовательность обновления:
# 1. Подключаемся к серверу
ssh root@194.67.84.241
# 2. Переходим в директорию проекта
cd /opt/snee-graf
# 3. Смотрим текущее состояние (опционально)
docker-compose ps
# 4. Останавливаем и удаляем контейнеры
docker-compose down
# 5. Удаляем старые образы
docker rmi end2040/snee-backend:latest end2040/snee-frontend:latest
# 6. Загружаем новые образы
docker-compose pull
# 7. Запускаем новые контейнеры
docker-compose up -d
# 8. Проверяем логи
docker-compose logs -f

# (Для выхода из логов: Ctrl+C)

# 9. Проверяем работу
curl http://localhost:8001/api/v1/health
curl http://localhost:3001

# 10. Очищаем неиспользуемые образы (освобождаем место)
docker image prune -f

⚠️ Важно:
docker-compose down останавливает И удаляет контейнеры, но НЕ удаляет образы
Если не удалить старые образы перед pull, Docker может не загрузить новые (если теги одинаковые)
После docker-compose up -d контейнеры запустятся в фоновом режиме (detached mode)