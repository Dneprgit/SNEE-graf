# 🛠️ Скрипты автоматизации SNЭЭ Graf

**Полезные bash скрипты для управления проектом на сервере**

---

## 📁 Список скриптов

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| `install-server.sh` | Первоначальная установка на чистый сервер | `sudo ./install-server.sh` |
| `check-status.sh` | Проверка статуса всех компонентов | `./check-status.sh` |
| `update.sh` | Обновление до новой версии | `./update.sh` |
| `restart.sh` | Перезапуск сервисов | `./restart.sh [backend\|frontend\|all]` |
| `logs.sh` | Просмотр логов | `./logs.sh [backend\|frontend\|nginx\|all]` |

---

## 📋 Подробное описание

### 1. install-server.sh

**Назначение:** Автоматическая установка проекта на новый сервер.

**Что делает:**
- ✅ Обновляет систему
- ✅ Устанавливает Docker и Docker Compose (если не установлены)
- ✅ Создает директории проекта
- ✅ Создает docker-compose.yml с вашим Docker Hub username
- ✅ Скачивает и запускает контейнеры
- ✅ Проверяет работоспособность

**Использование:**

```bash
# Запуск с правами root
sudo ./install-server.sh

# Или через curl (если скрипт на GitHub)
curl -sSL https://raw.githubusercontent.com/your-repo/main/web/scripts/install-server.sh | sudo bash
```

**Требует ввода:**
- Docker Hub username

**Результат:**
- Проект установлен в `/opt/snee-graf/`
- Контейнеры запущены
- Готов к настройке Nginx

---

### 2. check-status.sh

**Назначение:** Комплексная проверка статуса всех компонентов системы.

**Что проверяет:**
- ✅ Docker установлен и запущен
- ✅ Статус контейнеров (snee-backend, snee-frontend)
- ✅ Health checks контейнеров
- ✅ API endpoints (backend health, frontend)
- ✅ Nginx статус и конфигурация
- ✅ Использование ресурсов (CPU, RAM, Disk)
- ✅ SSL сертификаты
- ✅ Последние ошибки в логах

**Использование:**

```bash
./check-status.sh
```

**Пример вывода:**

```
╔════════════════════════════════════════════════════╗
║       SNЭЭ Graf - Проверка статуса системы        ║
╚════════════════════════════════════════════════════╝

═══ Docker ═══
✓ Docker установлен
✓ Docker daemon запущен

═══ Контейнеры ═══
NAMES           STATUS          PORTS
snee-backend    Up 2 hours      0.0.0.0:8001->8001/tcp
snee-frontend   Up 2 hours      0.0.0.0:8000->80/tcp

═══ Health Checks ═══
✓ Backend контейнер: Running
✓ Frontend контейнер: Running

═══ API Endpoints ═══
✓ Backend API (/api/v1/health): HTTP 200
✓ Frontend (http://localhost:3001): HTTP 200

═══ Nginx ═══
✓ Nginx: Active
✓ Nginx конфигурация: OK

═══ Использование ресурсов ═══
NAME            CPU %    MEM USAGE / LIMIT
snee-backend    0.50%    150MiB / 2GiB
snee-frontend   0.10%    50MiB / 2GiB

Использование диска:
Использовано: 8.5G из 50G (18%)

═══ SSL Сертификаты ═══
✓ SSL сертификат найден
Expiry Date: 2025-03-01 12:00:00+00:00 (VALID: 89 days)
```

**Рекомендация:** Добавьте в cron для периодической проверки.

---

### 3. update.sh

**Назначение:** Безопасное обновление проекта до новой версии.

**Что делает:**
- ✅ Проверяет текущее состояние
- ✅ Создает backup конфигураций
- ✅ Скачивает новые образы из Docker Hub
- ✅ Пересоздает контейнеры
- ✅ Ждет запуска сервисов (30 сек)
- ✅ Проверяет работоспособность
- ✅ Удаляет старые образы

**Использование:**

```bash
./update.sh
```

**Пример вывода:**

```
╔════════════════════════════════════════════════════╗
║          SNЭЭ Graf - Обновление проекта           ║
╚════════════════════════════════════════════════════╝

[1/6] Проверка текущего состояния...
[2/6] Создание backup текущих контейнеров...
✓ Backup создан: /opt/snee-graf/backups/backup-20250107-143022.tar.gz

[3/6] Загрузка новых образов из Docker Hub...
Pulling snee-backend ... done
Pulling snee-frontend ... done
✓ Образы успешно загружены

[4/6] Пересоздание и перезапуск контейнеров...
Recreating snee-backend ... done
Recreating snee-frontend ... done
✓ Контейнеры пересозданы

[5/6] Ожидание запуска сервисов (30 секунд)...

[6/6] Проверка работоспособности...
Backend API: ✓ OK (HTTP 200)
Frontend: ✓ OK (HTTP 200)

[Очистка] Удаление старых образов...
✓ Старые образы удалены

════════════════════════════════════════════════════
Обновление завершено успешно!
════════════════════════════════════════════════════
```

**Восстановление из backup (если что-то пошло не так):**

```bash
cd /opt/snee-graf
docker-compose down
tar -xzf backups/backup-YYYYMMDD-HHMMSS.tar.gz
docker-compose up -d
```

---

### 4. restart.sh

**Назначение:** Быстрый перезапуск сервисов.

**Использование:**

```bash
# Перезапустить все сервисы
./restart.sh all

# Перезапустить только backend
./restart.sh backend

# Перезапустить только frontend
./restart.sh frontend
```

**Что делает:**
- Перезапускает выбранные контейнеры
- Ждет 5 секунд
- Проверяет работоспособность
- Показывает статус

**Когда использовать:**
- После изменения конфигурации
- При нестабильной работе сервиса
- Для применения настроек

---

### 5. logs.sh

**Назначение:** Удобный просмотр логов различных компонентов.

**Использование:**

```bash
# Логи backend (FastAPI)
./logs.sh backend

# Логи frontend (React/Nginx)
./logs.sh frontend

# Логи Nginx (access + error)
./logs.sh nginx

# Логи всех контейнеров
./logs.sh all
```

**Что показывает:**
- **backend**: Логи FastAPI (запросы, ошибки, расчеты)
- **frontend**: Логи Nginx внутри контейнера
- **nginx**: Логи основного Nginx (access и error)
- **all**: Все логи в реальном времени

**Выход из режима просмотра:** `Ctrl+C`

---

## 🚀 Установка скриптов на сервер

### Вариант 1: Ручное копирование

```bash
# На локальном компьютере (Windows PowerShell)
scp -r "C:\den\Cursor\SNEE graf\web\scripts" root@194.67.84.241:/opt/snee-graf/

# На сервере
cd /opt/snee-graf/scripts
chmod +x *.sh
```

### Вариант 2: Через Git

```bash
# На сервере
cd /opt/snee-graf
git clone https://your-repo-url.git temp
mv temp/web/scripts .
rm -rf temp
chmod +x scripts/*.sh
```

### Вариант 3: Создать вручную

```bash
# На сервере
cd /opt/snee-graf
mkdir scripts
cd scripts

# Создайте каждый скрипт через nano
nano check-status.sh
# (вставьте содержимое)

# Сделайте исполняемым
chmod +x *.sh
```

---

## ⚙️ Автоматизация через Cron

### Регулярная проверка статуса

```bash
# Открыть crontab
crontab -e

# Добавить задачи
# Проверка каждый час
0 * * * * /opt/snee-graf/scripts/check-status.sh >> /var/log/snee-graf-check.log 2>&1

# Автообновление каждую ночь в 3:00
0 3 * * * /opt/snee-graf/scripts/update.sh >> /var/log/snee-graf-update.log 2>&1
```

### Мониторинг с отправкой уведомлений

```bash
# Проверка каждые 15 минут и уведомление при ошибках
*/15 * * * * /opt/snee-graf/scripts/check-status.sh | grep -i "✗" && echo "SNEE Graf: Ошибка обнаружена!" | mail -s "Alert: SNEE Graf" admin@example.com
```

---

## 🔧 Создание алиасов (для удобства)

Добавьте в `~/.bashrc` или `~/.bash_aliases`:

```bash
# SNEE Graf алиасы
alias snee-status='cd /opt/snee-graf && ./scripts/check-status.sh'
alias snee-logs='cd /opt/snee-graf && ./scripts/logs.sh'
alias snee-restart='cd /opt/snee-graf && ./scripts/restart.sh'
alias snee-update='cd /opt/snee-graf && ./scripts/update.sh'
alias snee-cd='cd /opt/snee-graf'
```

Применить:

```bash
source ~/.bashrc
```

Теперь можно использовать:

```bash
snee-status
snee-logs backend
snee-restart all
snee-update
```

---

## 📊 Примеры использования

### Типичный workflow обновления

```bash
# 1. Проверка текущего состояния
./check-status.sh

# 2. Обновление проекта
./update.sh

# 3. Просмотр логов для проверки
./logs.sh all

# 4. Финальная проверка
./check-status.sh
```

### Диагностика проблем

```bash
# 1. Проверка статуса
./check-status.sh

# 2. Если backend падает, смотрим логи
./logs.sh backend

# 3. Перезапускаем
./restart.sh backend

# 4. Проверяем снова
./check-status.sh
```

### Ежедневное обслуживание

```bash
# Утренняя проверка
./check-status.sh

# Если есть обновления
./update.sh

# Просмотр статистики
docker stats --no-stream
df -h
```

---

## 🛡️ Безопасность

### Права доступа

```bash
# Устанавливаем правильные права
chmod 755 /opt/snee-graf/scripts/*.sh
chown root:root /opt/snee-graf/scripts/*.sh
```

### Ограничение выполнения

Только определенные пользователи могут запускать скрипты:

```bash
# Создаем группу
groupadd snee-admins

# Добавляем пользователя
usermod -aG snee-admins username

# Устанавливаем права
chgrp snee-admins /opt/snee-graf/scripts/*.sh
chmod 750 /opt/snee-graf/scripts/*.sh
```

---

## 📝 Логирование

### Ведение логов выполнения скриптов

```bash
# Создать директорию для логов
mkdir -p /var/log/snee-graf

# Запуск с логированием
./check-status.sh | tee -a /var/log/snee-graf/status-$(date +%Y%m%d).log
./update.sh | tee -a /var/log/snee-graf/update-$(date +%Y%m%d).log
```

### Ротация логов

Создайте `/etc/logrotate.d/snee-graf`:

```
/var/log/snee-graf/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 🐛 Решение проблем

### Скрипт не запускается

```bash
# Проверьте права
ls -l /opt/snee-graf/scripts/

# Сделайте исполняемым
chmod +x /opt/snee-graf/scripts/*.sh

# Проверьте интерпретатор
head -1 /opt/snee-graf/scripts/check-status.sh
# Должно быть: #!/bin/bash
```

### Ошибка "command not found"

```bash
# Убедитесь, что вы в правильной директории
cd /opt/snee-graf/scripts

# Или используйте полный путь
/opt/snee-graf/scripts/check-status.sh
```

### Ошибка "Permission denied"

```bash
# Запустите с sudo (если нужны права root)
sudo ./check-status.sh

# Или добавьте себя в нужную группу
sudo usermod -aG docker $USER
# Перелогиньтесь для применения
```

---

## 📚 Дополнительная информация

- [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md) - Полная инструкция по развертыванию
- [COMMANDS.md](../COMMANDS.md) - Шпаргалка по командам
- [QUICKSTART_DOCKER.md](../QUICKSTART_DOCKER.md) - Быстрый старт

---

**💡 Совет:** Настройте алиасы и добавьте check-status.sh в cron для автоматического мониторинга!

