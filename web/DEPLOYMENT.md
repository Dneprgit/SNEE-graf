# Инструкция по развертыванию на Reg.ru

Это подробное руководство по развертыванию СНЭЭ Graf на сервере Reg.ru.

## Предварительные требования

- VPS или виртуальный хостинг с поддержкой Python 3.11+ и Node.js 18+
- Доступ по SSH
- Доменное имя (опционально, но рекомендуется)

## Вариант 1: Развертывание на VPS (рекомендуется)

### Шаг 1: Подключение к серверу

```bash
ssh user@your-server-ip
```

### Шаг 2: Установка необходимого ПО

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Установка Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Установка Nginx
sudo apt install nginx -y

# Установка Git
sudo apt install git -y
```

### Шаг 3: Клонирование проекта

```bash
cd /var/www
sudo git clone https://github.com/your-repo/snee-graf.git
sudo chown -R $USER:$USER snee-graf
cd snee-graf/web
```

### Шаг 4: Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp env.example .env
nano .env  # Отредактируйте параметры при необходимости
```

### Шаг 5: Настройка автозапуска Backend (systemd)

Создайте файл службы:

```bash
sudo nano /etc/systemd/system/snee-backend.service
```

Содержимое файла:

```ini
[Unit]
Description=SNEE Graf FastAPI Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/snee-graf/web/backend
Environment="PATH=/var/www/snee-graf/web/backend/venv/bin"
ExecStart=/var/www/snee-graf/web/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите службу:

```bash
sudo systemctl daemon-reload
sudo systemctl enable snee-backend
sudo systemctl start snee-backend
sudo systemctl status snee-backend
```

### Шаг 6: Настройка Frontend

```bash
cd ../frontend

# Установка зависимостей
npm install

# Создание production сборки
npm run build
```

### Шаг 7: Настройка Nginx

Скопируйте конфигурацию:

```bash
sudo cp ../nginx.conf /etc/nginx/sites-available/snee-graf
```

Отредактируйте конфигурацию:

```bash
sudo nano /etc/nginx/sites-available/snee-graf
```

Замените `your-domain.ru` на ваш реальный домен.

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/snee-graf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 8: Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d your-domain.ru -d www.your-domain.ru

# Автообновление сертификата
sudo systemctl enable certbot.timer
```

### Шаг 9: Настройка файрвола

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Вариант 2: Развертывание с Docker

### Шаг 1: Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose -y

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### Шаг 2: Запуск с Docker Compose

```bash
cd /var/www/snee-graf/web

# Запуск контейнеров
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Вариант 3: Развертывание на виртуальном хостинге Reg.ru

### Ограничения виртуального хостинга:

- Может не поддерживать FastAPI/Uvicorn
- Ограниченный доступ к системе
- Рекомендуется использовать VPS

Если у вас виртуальный хостинг с поддержкой Python:

1. Загрузите файлы через FTP/FileManager
2. Используйте `.htaccess` для проксирования запросов
3. Запустите backend через cron или passenger
4. Разместите frontend в public_html

## Обслуживание и мониторинг

### Просмотр логов Backend

```bash
sudo journalctl -u snee-backend -f
```

### Просмотр логов Nginx

```bash
sudo tail -f /var/log/nginx/snee-graf-access.log
sudo tail -f /var/log/nginx/snee-graf-error.log
```

### Перезапуск сервисов

```bash
# Backend
sudo systemctl restart snee-backend

# Nginx
sudo systemctl restart nginx
```

### Обновление приложения

```bash
cd /var/www/snee-graf
git pull origin main

# Backend
cd web/backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart snee-backend

# Frontend
cd ../frontend
npm install
npm run build
```

## Решение проблем

### Backend не запускается

```bash
# Проверьте логи
sudo journalctl -u snee-backend -n 50

# Проверьте права доступа
sudo chown -R www-data:www-data /var/www/snee-graf/web/backend

# Проверьте виртуальное окружение
cd /var/www/snee-graf/web/backend
source venv/bin/activate
python -c "import fastapi; print(fastapi.__version__)"
```

### Nginx возвращает 502 Bad Gateway

```bash
# Убедитесь, что backend запущен
sudo systemctl status snee-backend

# Проверьте, что backend слушает на порту 8001
sudo netstat -tlnp | grep 8001

# Проверьте логи Nginx
sudo tail -f /var/log/nginx/error.log
```

### Frontend не отображается

```bash
# Проверьте, что файлы собраны
ls -la /var/www/snee-graf/web/frontend/dist/

# Проверьте права доступа
sudo chown -R www-data:www-data /var/www/snee-graf/web/frontend/dist

# Пересоберите frontend
cd /var/www/snee-graf/web/frontend
npm run build
```

## Оптимизация производительности

### 1. Кэширование в Nginx

Уже настроено в nginx.conf для статических ресурсов.

### 2. Увеличение workers для Backend

В файле `/etc/systemd/system/snee-backend.service` измените:

```ini
ExecStart=/var/www/snee-graf/web/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --workers 8
```

### 3. Настройка кэша приложения

Добавьте Redis для кэширования результатов расчетов (опционально).

## Безопасность

1. **Регулярно обновляйте систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Используйте HTTPS (SSL):**
Обязательно настройте SSL сертификат.

3. **Ограничьте доступ к API:**
В backend добавьте rate limiting и аутентификацию при необходимости.

4. **Настройте файрвол:**
Откройте только необходимые порты (80, 443, 22).

5. **Регулярные бэкапы:**
```bash
# Бэкап базы данных (если используется)
# Бэкап файлов конфигурации
sudo tar -czf snee-backup-$(date +%Y%m%d).tar.gz /var/www/snee-graf
```

## Контакты и поддержка

При возникновении проблем с развертыванием создайте issue в репозитории проекта.

