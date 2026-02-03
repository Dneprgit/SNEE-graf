# 🚀 Развертывание на сервере

Этот файл содержит инструкции по развертыванию **двух проектов** одновременно:
- **dneprovskii.ru** - старый проект (порты 8001, 3001)
- **so-spes.ru** - новый проект (порты 8002, 3002)

---

## 📦 Docker образы

### Для создания Docker образов и запуска контейнеров используем на сервере скрипт:

install-server-new.sh 

в директории root.

Если скрипт не подходит делаем установку Docker в ручную, алгоритм описан ниже.

Для проверки работы контейнеров запускаем скрипт:

check-health-new.sh


### Старый проект (dneprovskii.ru):
- ✅ `end2040/snee-backend:latest`
- ✅ `end2040/snee-frontend:latest`

### Новый проект (so-spes.ru):
- ✅ `end2040/snee_web_spes-backend:latest`
- ✅ `end2040/snee_web_spes-frontend:latest`

---

## 📋 Пошаговая инструкция

### 1. Подключитесь к серверу

```bash
ssh root@YOUR_SERVER_IP
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

Вставьте содержимое:

```yaml
version: '3.8'

services:
  # ==========================================
  # Проект dneprovskii.ru (порты 8001, 3001)
  # ==========================================
  snee-backend-old:
    image: end2040/snee-backend:latest
    container_name: snee-backend-old
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

  snee-frontend-old:
    image: end2040/snee-frontend:latest
    container_name: snee-frontend-old
    restart: always
    ports:
      - "3001:80"
    networks:
      - snee-network
    depends_on:
      - snee-backend-old
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  # ==========================================
  # Проект so-spes.ru (порты 8002, 3002)
  # ==========================================
  snee-backend-spes:
    image: end2040/snee_web_spes-backend:latest
    container_name: snee-backend-spes
    restart: always
    ports:
      - "8002:8002"
    environment:
      - PYTHONUNBUFFERED=1
      - ENVIRONMENT=production
    networks:
      - snee-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  snee-frontend-spes:
    image: end2040/snee_web_spes-frontend:latest
    container_name: snee-frontend-spes
    restart: always
    ports:
      - "3002:80"
    networks:
      - snee-network
    depends_on:
      - snee-backend-spes
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

# Проверка старого проекта (dneprovskii.ru)
curl http://localhost:8001/api/v1/health
curl http://localhost:3001

# Проверка нового проекта (so-spes.ru)
curl http://localhost:8002/api/v1/health
curl http://localhost:3002

# Логи
docker-compose logs -f
```

---

## 🌐 Настройка Nginx

### сначала установите на сервере Nginx, и папка /etc/nginx/sites-available появится сама.
Команды:

sudo apt update

sudo apt install -y nginx

Проверка:

nginx -v

ls /etc/nginx/sites-available

### 1. Создайте конфигурацию Nginx

```bash
sudo nano /etc/nginx/sites-available/snee-graf
```

Вставьте содержимое из файла `nginx-server.conf` (см. в проекте): для вставки, нажать правую кнопку мыши или нажать shift+insert, далее ^X, далее y, далее Enter.



### 2. Активируйте конфигурацию

```bash
# Создайте символическую ссылку
sudo ln -sf /etc/nginx/sites-available/snee-graf /etc/nginx/sites-enabled/

# Проверьте конфигурацию
sudo nginx -t

# Перезагрузите Nginx
sudo systemctl reload nginx
```

### 3. Настройте DNS

Убедитесь, что DNS записи указывают на ваш сервер:

```
A     dneprovskii.ru      → [IP сервера]
A     www.dneprovskii.ru  → [IP сервера]
A     so-spes.ru          → [IP сервера]
A     www.so-spes.ru      → [IP сервера]
```

### 4. Получите SSL сертификаты

Получи SSL сертификаты so-spes.ru www.so-spes.ru

метод certbot, на этом сервере, доступ посмотри во вложении@nginx-server.conf , веб-сервер nginx, сохранить посмотри в @nginx-server.conf 

Сертификаты могу получить только на самом сервере (нужны запись в /etc/letsencrypt и доступ к сети/портам). Ниже команды, которые нужно выполнить на сервере с этим nginx (у вас уже есть ACME webroot в конфиге):
1) Подготовить webroot и проверить nginx:
sudo mkdir -p /var/www/certbot
sudo nginx -t && sudo systemctl reload nginx
2) Выпустить сертификаты для so-spes.ru и www.so-spes.ru:
sudo certbot certonly --webroot -w /var/www/certbot -d so-spes.ru -d www.so-spes.ru --agree-tos -m you@example.com --no-eff-email
3) Проверить наличие файлов:
sudo ls /etc/letsencrypt/live/so-spes.ru/
4) Перезагрузить nginx:
sudo systemctl reload nginx
Если выпуск не пройдет — обычно причина в DNS (A/AAAA должны указывать на сервер) или закрытом порте 80.










### Установить Certbot:

sudo apt install certbot python3-certbot-nginx


### Получите SSL сертификаты
```bash
# Для dneprovskii.ru (если ещё не получен)
sudo certbot --nginx -d dneprovskii.ru -d www.dneprovskii.ru

# Для so-spes.ru
sudo certbot --nginx -d so-spes.ru -d www.so-spes.ru
```

---

## ✅ Проверка работоспособности

После всех настроек проверьте оба сайта:

### Проверка dneprovskii.ru (старый проект):

```bash
# API через Nginx
curl https://dneprovskii.ru/api/v1/health

# Frontend через браузер
https://dneprovskii.ru
```

### Проверка so-spes.ru (новый проект):

```bash
# API через Nginx
curl https://so-spes.ru/api/v1/health

# Frontend через браузер
https://so-spes.ru
```

---

## 📊 Статус контейнеров

Должны быть запущены 4 контейнера:

```bash
docker ps

# Ожидаемый результат:
# snee-backend-old     (порт 8001)
# snee-frontend-old    (порт 3001)
# snee-backend-spes    (порт 8002)
# snee-frontend-spes   (порт 3002)
```

---

## 🔄 Обновление проектов

### Обновление старого проекта (dneprovskii.ru):

```bash
cd /opt/snee-graf
docker-compose stop snee-backend-old snee-frontend-old
docker-compose rm -f snee-backend-old snee-frontend-old
docker rmi end2040/snee-backend:latest end2040/snee-frontend:latest
docker-compose pull snee-backend-old snee-frontend-old
docker-compose up -d snee-backend-old snee-frontend-old
```

### Обновление нового проекта (so-spes.ru):

```bash
cd /opt/snee-graf
docker-compose stop snee-backend-spes snee-frontend-spes

docker-compose stop snee-backend-spes
docker-compose stop snee-frontend-spes
docker-compose rm -f snee-backend-spes snee-frontend-spes
docker-compose rm -f snee-backend-spes 
docker-compose rm -f snee-frontend-spes

docker rmi end2040/snee_web_spes-backend:latest end2040/snee_web_spes-frontend:latest
docker rmi end2040/snee_web_spes-backend:latest
docker rmi end2040/snee_web_spes-frontend:latest
docker-compose pull snee-backend-spes snee-frontend-spes
docker-compose pull snee-backend-spes
docker-compose pull snee-frontend-spes

docker-compose up -d snee-backend-spes snee-frontend-spes
docker-compose up -d snee-backend-spes
docker-compose up -d snee-frontend-spes
```

### Обновление обоих проектов сразу:

```bash
cd /opt/snee-graf
docker-compose down
docker rmi end2040/snee-backend:latest end2040/snee-frontend:latest \
           end2040/snee_web_spes-backend:latest end2040/snee_web_spes-frontend:latest
docker-compose pull
docker-compose up -d
```

---

## 🧹 Полезные команды

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только старый проект
docker-compose logs -f snee-backend-old snee-frontend-old

# Только новый проект
docker-compose logs -f snee-backend-spes snee-frontend-spes

# Последние 50 строк
docker-compose logs --tail=50
```

### Перезапуск контейнеров

```bash
# Перезапустить все
docker-compose restart

# Перезапустить только старый проект
docker-compose restart snee-backend-old snee-frontend-old

# Перезапустить только новый проект
docker-compose restart snee-backend-spes snee-frontend-spes
```

### Проверка здоровья

```bash
# Статус всех контейнеров
docker-compose ps

# Health check API старого проекта
curl http://localhost:8001/api/v1/health

# Health check API нового проекта
curl http://localhost:8002/api/v1/health
```

### Очистка

```bash
# Удалить неиспользуемые образы
docker image prune -f

# Удалить неиспользуемые контейнеры
docker container prune -f

# Посмотреть использование диска
docker system df
```

---

## 🔧 Решение проблем

### Порт уже занят

Если порт занят, найдите процесс:

```bash
sudo lsof -i :8001
sudo lsof -i :8002
sudo lsof -i :3001
sudo lsof -i :3002
```

### Контейнер не запускается

```bash
# Проверьте логи конкретного контейнера
docker logs snee-backend-old
docker logs snee-backend-spes

# Проверьте образы
docker images | grep snee
```

### Nginx не может подключиться

```bash
# Проверьте, что все контейнеры запущены
docker ps | grep snee

# Проверьте, что порты слушаются
netstat -tulpn | grep 8001
netstat -tulpn | grep 8002
netstat -tulpn | grep 3001
netstat -tulpn | grep 3002

# Проверьте логи Nginx
sudo tail -f /var/log/nginx/snee-dneprovskii-error.log
sudo tail -f /var/log/nginx/snee-spes-error.log

# Перезапустите Nginx
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📚 Дополнительная документация

- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - полная пошаговая инструкция
- **[MIGRATION_TO_SO-SPES.md](MIGRATION_TO_SO-SPES.md)** - инструкция по миграции на новый домен
- **[PORTS_INFO.md](PORTS_INFO.md)** - информация о портах
- **[nginx-server.conf](nginx-server.conf)** - конфигурация Nginx

---

## 📝 Архитектура

```
Сервер Reg.ru
├── Docker Containers
│   ├── snee-backend-old    (dneprovskii.ru:8001)
│   ├── snee-frontend-old   (dneprovskii.ru:3001)
│   ├── snee-backend-spes   (so-spes.ru:8002)
│   └── snee-frontend-spes  (so-spes.ru:3002)
│
└── Nginx
    ├── dneprovskii.ru      → 127.0.0.1:8001/3001
    └── so-spes.ru          → 127.0.0.1:8002/3002
```

---

**Оба проекта могут работать одновременно! 🎉**


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

docker stop end2040/snee_web_spes-backend

docker stop end2040/snee_web_spes-frontend



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