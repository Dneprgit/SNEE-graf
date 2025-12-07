# 📑 Индекс документации Docker развертывания

**Быстрая навигация по всем файлам и документам**

---

## 🚀 Начните здесь

### Первое развертывание
👉 **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - краткий обзор того, что создано

### Детальная инструкция
👉 **[README_DOCKER.md](README_DOCKER.md)** - главный обзор процесса  
👉 **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - пошаговая инструкция (1000+ строк)

### Быстрый деплой
👉 **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)** - для опытных пользователей

---

## 📖 Основная документация

| Файл | Описание | Когда читать |
|------|----------|--------------|
| [README_DOCKER.md](README_DOCKER.md) | Обзор Docker развертывания | Сначала для общей картины |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Полная инструкция (7 частей) | При первом развертывании |
| [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) | Быстрая версия | Когда знаете процесс |
| [COMMANDS.md](COMMANDS.md) | Справочник всех команд | Для быстрого поиска |
| [DOCKER_FILES_SUMMARY.md](DOCKER_FILES_SUMMARY.md) | Описание всех файлов | Для понимания структуры |
| [PORTS_INFO.md](PORTS_INFO.md) | Всё о портах проекта | При настройке сети |
| [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) | Итоговый обзор | Для общего понимания |

---

## 🐳 Docker файлы

| Файл | Описание | Использование |
|------|----------|---------------|
| [Dockerfile.backend.prod](Dockerfile.backend.prod) | Production образ FastAPI | `docker build -f ...` |
| [Dockerfile.frontend.prod](Dockerfile.frontend.prod) | Production образ React | `docker build -f ...` |
| [docker-compose.prod.yml](docker-compose.prod.yml) | Production конфигурация | `docker-compose -f ...` |
| [docker-compose.yml](docker-compose.yml) | Development конфигурация | Для локальной разработки |
| [.dockerignore](.dockerignore) | Исключения для build | Автоматически |

---

## 🌐 Конфигурации

| Файл | Описание | Расположение |
|------|----------|--------------|
| [nginx-server.conf](nginx-server.conf) | Production Nginx конфиг | `/etc/nginx/sites-available/snee-graf` |
| [nginx.conf](nginx.conf) | Development Nginx конфиг | Для локальной разработки |
| [backend/env.example.prod](backend/env.example.prod) | Пример переменных backend | Скопировать в `backend/.env` |
| [frontend/env.example.prod](frontend/env.example.prod) | Пример переменных frontend | Скопировать в `frontend/.env` |

---

## 🛠️ Скрипты автоматизации

| Скрипт | Назначение | Команда |
|--------|------------|---------|
| [scripts/install-server.sh](scripts/install-server.sh) | Первоначальная установка | `sudo ./install-server.sh` |
| [scripts/check-status.sh](scripts/check-status.sh) | Проверка всех компонентов | `./check-status.sh` |
| [scripts/update.sh](scripts/update.sh) | Обновление проекта | `./update.sh` |
| [scripts/restart.sh](scripts/restart.sh) | Перезапуск сервисов | `./restart.sh [service]` |
| [scripts/logs.sh](scripts/logs.sh) | Просмотр логов | `./logs.sh [service]` |
| [scripts/README.md](scripts/README.md) | Документация скриптов | Для справки |

---

## 📚 Дополнительная документация

| Файл | Описание | Тип |
|------|----------|-----|
| [README.md](README.md) | Главная документация проекта | Общая |
| [QUICKSTART.md](QUICKSTART.md) | Быстрый старт для разработки | Development |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Развертывание без Docker | Alternative |
| [API_EXAMPLES.md](API_EXAMPLES.md) | Примеры использования API | API |
| [TESTING.md](TESTING.md) | Руководство по тестированию | QA |
| [USER_GUIDE.md](USER_GUIDE.md) | Руководство пользователя | User |
| [SUMMARY.md](SUMMARY.md) | Общий обзор проекта | Overview |
| [CHANGELOG_Y_AXIS.md](CHANGELOG_Y_AXIS.md) | История изменений | History |

---

## 🔍 Быстрый поиск

### Хочу развернуть проект первый раз
→ [README_DOCKER.md](README_DOCKER.md) → [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

### Хочу быстро обновить
→ [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) → раздел "Обновление"

### Нужна конкретная команда
→ [COMMANDS.md](COMMANDS.md) → поиск по файлу (Ctrl+F)

### Не понимаю порты
→ [PORTS_INFO.md](PORTS_INFO.md)

### Хочу понять структуру файлов
→ [DOCKER_FILES_SUMMARY.md](DOCKER_FILES_SUMMARY.md)

### Что-то сломалось
→ [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) → раздел "Решение проблем"  
→ [COMMANDS.md](COMMANDS.md) → раздел "Диагностика"

### Хочу автоматизировать задачи
→ [scripts/README.md](scripts/README.md)

---

## 📋 Структура папок

```
web/
├── 📖 Документация Docker
│   ├── INDEX_DOCKER.md                 (этот файл)
│   ├── README_DOCKER.md                (начните здесь)
│   ├── DOCKER_DEPLOYMENT.md            (основная инструкция)
│   ├── QUICKSTART_DOCKER.md            (быстрый старт)
│   ├── COMMANDS.md                     (все команды)
│   ├── DOCKER_FILES_SUMMARY.md         (обзор файлов)
│   ├── PORTS_INFO.md                   (информация о портах)
│   └── DEPLOYMENT_SUMMARY.md           (итоговый обзор)
│
├── 🐳 Docker файлы
│   ├── Dockerfile.backend.prod
│   ├── Dockerfile.frontend.prod
│   ├── docker-compose.prod.yml
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── 🌐 Конфигурации
│   ├── nginx-server.conf               (production)
│   ├── nginx.conf                      (development)
│   ├── backend/env.example.prod
│   └── frontend/env.example.prod
│
├── 🛠️ Скрипты
│   └── scripts/
│       ├── README.md
│       ├── install-server.sh
│       ├── check-status.sh
│       ├── update.sh
│       ├── restart.sh
│       └── logs.sh
│
├── 📚 Остальная документация
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── DEPLOYMENT.md
│   ├── API_EXAMPLES.md
│   ├── TESTING.md
│   ├── USER_GUIDE.md
│   ├── SUMMARY.md
│   └── CHANGELOG_Y_AXIS.md
│
├── backend/                            (FastAPI)
└── frontend/                           (React)
```

---

## 🎯 Пути для разных задач

### Разработчик - первое знакомство
```
1. README.md (общая информация)
2. QUICKSTART.md (запуск для разработки)
3. API_EXAMPLES.md (использование API)
```

### DevOps - развертывание production
```
1. INDEX_DOCKER.md (этот файл - навигация)
2. README_DOCKER.md (обзор процесса)
3. DOCKER_DEPLOYMENT.md (детальная инструкция)
4. scripts/README.md (автоматизация)
5. COMMANDS.md (справочник команд)
```

### DevOps - обслуживание
```
1. QUICKSTART_DOCKER.md (быстрое обновление)
2. scripts/check-status.sh (проверка)
3. scripts/update.sh (обновление)
4. COMMANDS.md (команды для диагностики)
```

### Пользователь приложения
```
1. USER_GUIDE.md (руководство пользователя)
2. Веб-интерфейс: https://snee.companykd.world
```

---

## 🔢 Версии файлов

### Production (для сервера)
- `Dockerfile.backend.prod`
- `Dockerfile.frontend.prod`
- `docker-compose.prod.yml`
- `nginx-server.conf`
- `backend/env.example.prod`
- `frontend/env.example.prod`

### Development (для локальной разработки)
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `nginx.conf`
- `backend/env.example`
- `frontend/env.example`

---

## 📊 Статистика документации

- **Всего документов:** 8 основных + 6 скриптов
- **Объем:** 4000+ строк документации
- **Языки:** Markdown, Shell Script
- **Инструкции:** Пошаговые с примерами
- **Команды:** 100+ готовых команд с пояснениями

---

## ✅ Проверочный список

### Документация прочитана
- [ ] README_DOCKER.md
- [ ] DOCKER_DEPLOYMENT.md
- [ ] PORTS_INFO.md
- [ ] scripts/README.md

### Файлы подготовлены
- [ ] Dockerfile.backend.prod
- [ ] Dockerfile.frontend.prod
- [ ] docker-compose.prod.yml
- [ ] nginx-server.conf

### Скрипты готовы
- [ ] Все скрипты скопированы на сервер
- [ ] Права выполнения установлены (chmod +x)

### Конфигурация
- [ ] Docker Hub username известен
- [ ] Порты 8001 и 3001 свободны
- [ ] DNS записи настроены

---

## 🎓 Рекомендуемый порядок изучения

### День 1: Знакомство
1. [INDEX_DOCKER.md](INDEX_DOCKER.md) - навигация (этот файл)
2. [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - что создано
3. [README_DOCKER.md](README_DOCKER.md) - обзор процесса
4. [PORTS_INFO.md](PORTS_INFO.md) - понимание портов

### День 2: Подготовка
1. [DOCKER_FILES_SUMMARY.md](DOCKER_FILES_SUMMARY.md) - описание файлов
2. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - части 1-3
3. Подготовка локальной среды

### День 3: Развертывание
1. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - части 4-7
2. [scripts/README.md](scripts/README.md) - автоматизация
3. Развертывание на сервере

### После развертывания
1. [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) - для быстрых задач
2. [COMMANDS.md](COMMANDS.md) - держать под рукой

---

## 📞 Помощь и поддержка

### Проблемы с развертыванием
→ [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) раздел "Решение проблем"

### Проблемы с портами
→ [PORTS_INFO.md](PORTS_INFO.md) раздел "Решение проблем с портами"

### Проблемы со скриптами
→ [scripts/README.md](scripts/README.md) раздел "Решение проблем"

### Нужна команда
→ [COMMANDS.md](COMMANDS.md) → Ctrl+F для поиска

---

## 🔗 Полезные ссылки

### Внутренние ресурсы
- [Главный README](README.md)
- [API документация](API_EXAMPLES.md)
- [Тестирование](TESTING.md)

### Внешние ресурсы
- [Docker Documentation](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 🎉 Готово к использованию!

Вся документация готова. Начните с **[README_DOCKER.md](README_DOCKER.md)**

**Удачи в развертывании! 🚀**

---

*Версия: 1.0*  
*Дата: Декабрь 2024*  
*Проект: SNЭЭ Graf*

