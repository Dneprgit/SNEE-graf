# 🔄 Миграция на новый домен SO-SPES.RU

## Краткая информация

**Дата миграции:** Декабрь 2025  
**Новый домен:** so-spes.ru, www.so-spes.ru  
**Новые порты:** Frontend 3002, Backend 8002  
**Docker Hub репозиторий:** end2040/snee_web_spes

---

## Что было изменено

### 1. Docker конфигурации

#### docker-compose.yml (разработка)
- Backend порт: 8001 → **8002**
- Frontend порт: 3001 → **3002**
- API URL обновлен на http://localhost:8002

#### docker-compose.prod.yml (production с переменными)
- Репозиторий: ${DOCKER_USERNAME}/snee-backend → **end2040/snee_web_spes-backend**
- Репозиторий: ${DOCKER_USERNAME}/snee-frontend → **end2040/snee_web_spes-frontend**
- Backend порт: 8001:8001 → **8002:8002**
- Frontend порт: 3001:80 → **3002:80**

#### docker-compose.server.yml (production сервер)
- Репозиторий: end2040/snee-backend → **end2040/snee_web_spes-backend**
- Репозиторий: end2040/snee-frontend → **end2040/snee_web_spes-frontend**
- Backend порт: 8001:8001 → **8002:8002**
- Frontend порт: 3001:80 → **3002:80**

---

### 2. Nginx конфигурации

#### nginx-server.conf
- Домен: dneprovskii.ru → **so-spes.ru**
- Домен: www.dneprovskii.ru → **www.so-spes.ru**
- Backend upstream: 127.0.0.1:8001 → **127.0.0.1:8002**
- Frontend upstream: 127.0.0.1:3001 → **127.0.0.1:3002**
- SSL сертификаты: /etc/letsencrypt/live/dneprovskii.ru → **/etc/letsencrypt/live/so-spes.ru**

#### nginx.conf (базовая конфигурация)
- Домен: your-domain.ru → **so-spes.ru**
- Backend proxy: 127.0.0.1:8001 → **127.0.0.1:8002**
- Все proxy_pass обновлены на новый порт

---

### 3. Environment файлы

#### Backend (web/backend/)
**env.example:**
- PORT: 8001 → **8002**
- ALLOWED_ORIGINS: http://localhost:3001 → **http://localhost:3002**

**env.example.prod:**
- ALLOWED_ORIGINS: https://snee.companykd.world → **https://so-spes.ru,https://www.so-spes.ru**

#### Frontend (web/frontend/)
**env.example:**
- VITE_API_URL: http://localhost:8001 → **http://localhost:8002**

**env.example.prod:**
- VITE_API_URL: https://snee.companykd.world/api → **https://so-spes.ru/api**

---

### 4. Dockerfiles

#### Dockerfile.backend.prod
- EXPOSE: 8001 → **8002**
- CMD port: --port 8001 → **--port 8002**

#### backend/Dockerfile
- EXPOSE: 8001 → **8002**
- CMD port: --port 8001 → **--port 8002**

#### frontend/Dockerfile
- EXPOSE: 3001 → **3002**

---

### 5. Конфигурационные файлы

#### vite.config.js
- Server port: 3001 → **3002**
- Proxy target: http://localhost:8001 → **http://localhost:8002**

#### backend/main.py
- Uvicorn port: 8001 → **8002** (в блоке if __name__ == "__main__")

---

### 6. Скрипты

#### start-dev.bat (Windows)
- Backend port: --port 8001 → **--port 8002**
- Frontend URL: http://localhost:3001 → **http://localhost:3002**
- Backend URL: http://localhost:8001 → **http://localhost:8002**

#### start-dev.sh (Linux/Mac)
- Backend port: --port 8001 → **--port 8002**
- Все URL обновлены на новые порты

#### backend/run.bat
- Uvicorn port: --port 8001 → **--port 8002**

#### scripts/update.sh
- Backend health check: http://localhost:8001 → **http://localhost:8002**
- Frontend check: http://localhost:3001 → **http://localhost:3002**

#### scripts/check-status.sh
- Backend API check: http://localhost:8001 → **http://localhost:8002**
- Frontend check: http://localhost:3001 → **http://localhost:3002**
- SSL cert domain: snee.companykd.world → **so-spes.ru**

#### scripts/restart.sh
- Backend health: http://localhost:8001 → **http://localhost:8002**
- Frontend check: http://localhost:3001 → **http://localhost:3002**

#### scripts/install-server.sh
- Docker images: ${DOCKER_USERNAME}/snee-* → **${DOCKER_USERNAME}/snee_web_spes-***
- Все порты обновлены на 8002 и 3002

---

### 7. Документация

#### PORTS_INFO.md
- Все порты обновлены: 8001 → **8002**, 3001 → **3002**
- Домен: snee.companykd.world → **so-spes.ru**
- Добавлена информация о новом Docker Hub репозитории
- Обновлены все примеры команд и схемы

---

## Что нужно сделать для деплоя

### 1. Подготовка .env файлов

**Backend (.env):**
```bash
HOST=0.0.0.0
PORT=8002
ENVIRONMENT=production
ALLOWED_ORIGINS=https://so-spes.ru,https://www.so-spes.ru
LOG_LEVEL=INFO
```

**Frontend (.env):**
```bash
VITE_API_URL=https://so-spes.ru/api
VITE_APP_TITLE=СНЭЭ Graf
VITE_MODE=production
```

### 2. Сборка и пуш Docker образов

```bash
# Backend
cd web
docker build -f Dockerfile.backend.prod -t end2040/snee_web_spes-backend:latest .
docker push end2040/snee_web_spes-backend:latest

# Frontend
docker build -f Dockerfile.frontend.prod -t end2040/snee_web_spes-frontend:latest .
docker push end2040/snee_web_spes-frontend:latest
```

### 3. На сервере

#### 3.1 Остановить старые контейнеры (если есть)
```bash
cd /opt/snee-graf
docker-compose down
```

#### 3.2 Скопировать docker-compose.server.yml
```bash
# Скопируйте содержимое web/docker-compose.server.yml на сервер
```

#### 3.3 Настроить Nginx
```bash
# Скопируйте web/nginx-server.conf в /etc/nginx/sites-available/snee-graf
sudo cp nginx-server.conf /etc/nginx/sites-available/snee-graf
sudo ln -sf /etc/nginx/sites-available/snee-graf /etc/nginx/sites-enabled/

# Проверка конфигурации
sudo nginx -t

# Перезапуск
sudo systemctl reload nginx
```

#### 3.4 Получить SSL сертификат
```bash
sudo certbot --nginx -d so-spes.ru -d www.so-spes.ru
```

#### 3.5 Запустить контейнеры
```bash
docker-compose -f docker-compose.server.yml pull
docker-compose -f docker-compose.server.yml up -d
```

#### 3.6 Проверка
```bash
# Статус контейнеров
docker ps

# Проверка backend
curl http://localhost:8002/api/v1/health

# Проверка frontend
curl http://localhost:3002

# Проверка через домен
curl https://so-spes.ru/api/v1/health
curl https://so-spes.ru
```

---

## DNS настройки

Убедитесь, что DNS записи для домена so-spes.ru указывают на IP вашего сервера:

```
A     so-spes.ru      → [IP сервера]
A     www.so-spes.ru  → [IP сервера]
```

---

## Проверочный список

- [ ] .env файлы созданы и заполнены
- [ ] Docker образы собраны и загружены на Docker Hub
- [ ] docker-compose.server.yml скопирован на сервер
- [ ] Nginx конфигурация обновлена
- [ ] DNS записи настроены
- [ ] SSL сертификат получен
- [ ] Контейнеры запущены и работают
- [ ] Backend отвечает на /api/v1/health
- [ ] Frontend доступен через домен
- [ ] API работает через https://so-spes.ru/api

---

## Откат (если что-то пошло не так)

Если нужно вернуться к старой конфигурации:

```bash
# Остановить новые контейнеры
docker-compose down

# Использовать старую конфигурацию
# (сохраните backup старых файлов перед миграцией)
```

---

## Контакты для поддержки

При возникновении проблем проверьте:
- Логи контейнеров: `docker-compose logs -f`
- Логи Nginx: `sudo tail -f /var/log/nginx/snee-graf-error.log`
- Статус системы: `./scripts/check-status.sh`

---

**Миграция завершена успешно!** 🎉

