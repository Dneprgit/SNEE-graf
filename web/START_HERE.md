# 🚀 НАЧНИТЕ ЗДЕСЬ - SNЭЭ Graf

**Добро пожаловать в проект SNЭЭ Graf!**

---

## 🎯 Что это?

**SNЭЭ Graf** - современная веб-система визуализации диспетчерского графика работы системы накопления электрической энергии (СНЭЭ).

### Возможности:
✅ Интерактивные графики и визуализация  
✅ Расчет оптимального графика заряда/разряда  
✅ Загрузка данных из Excel  
✅ Экспорт результатов  
✅ Современный UI с Tailwind CSS и Framer Motion  

---

## 🧭 Выберите свой путь

### 👨‍💻 Я разработчик - хочу работать с кодом

**Для локальной разработки:**

1. **[README.md](README.md)** - полная документация проекта
2. **[QUICKSTART.md](QUICKSTART.md)** - быстрый старт для разработки
3. **[API_EXAMPLES.md](API_EXAMPLES.md)** - примеры использования API
4. **[TESTING.md](TESTING.md)** - тестирование

**Быстрый запуск:**
```bash
# Backend
cd web/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Frontend (в другом терминале)
cd web/frontend
npm install
npm run dev
```

Откройте: http://localhost:3001

---

### 🚀 Я DevOps - хочу развернуть на сервере

**Для продакшен развертывания через Docker:**

1. **[INDEX_DOCKER.md](INDEX_DOCKER.md)** - 📑 навигация по Docker документации ⭐
2. **[README_DOCKER.md](README_DOCKER.md)** - 🐳 обзор Docker развертывания
3. **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - 📘 пошаговая инструкция (начните здесь!)
4. **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)** - ⚡ быстрый деплой
5. **[COMMANDS.md](COMMANDS.md)** - 📝 справочник команд

**Workflow:**
```
Локально: Сборка → Docker Hub → Сервер: Pull → Запуск → Nginx → SSL → Готово!
```

**Альтернатива без Docker:**
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - ручная установка

---

### 👤 Я пользователь - хочу использовать систему

**Руководства:**

1. **[USER_GUIDE.md](USER_GUIDE.md)** - руководство пользователя
2. Откройте веб-интерфейс: https://snee.companykd.world

**Что можно делать:**
- Загружать профиль баланса из Excel
- Настраивать параметры СНЭЭ
- Рассчитывать оптимальный график
- Визуализировать результаты
- Экспортировать данные

---

## 📊 Архитектура проекта

```
SNEE Graf
├── Desktop версия (PyQt6)          # Десктопное приложение
└── Web версия (FastAPI + React)    # Веб-приложение ⭐
    ├── Backend (FastAPI)
    │   ├── Алгоритм water-filling
    │   ├── REST API
    │   └── Загрузка Excel
    └── Frontend (React)
        ├── Интерактивные графики (Recharts)
        ├── SVG визуализация
        └── Современный UI (Tailwind)
```

---

## 🔌 Порты и доступ

### Локальная разработка
```
Backend:   http://localhost:8001
Frontend:  http://localhost:3001
API Docs:  http://localhost:8001/docs
```

### Production (сервер Reg.ru)
```
IP:        194.67.84.241
Backend:   http://194.67.84.241:8001
Frontend:  http://194.67.84.241:3001
Домен:     https://snee.companykd.world (через Nginx + SSL)
```

Подробнее: **[PORTS_INFO.md](PORTS_INFO.md)**

---

## 📚 Полная структура документации

### Для разработчиков
```
README.md                  # Главная документация
QUICKSTART.md              # Быстрый старт
API_EXAMPLES.md            # Примеры API
TESTING.md                 # Тестирование
```

### Для DevOps (Docker развертывание) ⭐
```
INDEX_DOCKER.md            # Навигация (начните здесь!)
README_DOCKER.md           # Обзор процесса
DOCKER_DEPLOYMENT.md       # Пошаговая инструкция
QUICKSTART_DOCKER.md       # Быстрый деплой
COMMANDS.md                # Все команды
DOCKER_FILES_SUMMARY.md    # Описание файлов
PORTS_INFO.md              # Информация о портах
DEPLOYMENT_SUMMARY.md      # Итоговый обзор
scripts/README.md          # Скрипты автоматизации
```

### Для пользователей
```
USER_GUIDE.md              # Руководство пользователя
```

### Дополнительно
```
SUMMARY.md                 # Общий обзор
CHANGELOG_Y_AXIS.md        # История изменений
DEPLOYMENT.md              # Развертывание без Docker
```

---

## 🛠️ Технологии

### Backend
- **FastAPI** - современный Python web framework
- **NumPy & Pandas** - вычисления и обработка данных
- **Uvicorn** - ASGI сервер
- **OpenPyXL** - работа с Excel

### Frontend
- **React 18** - UI библиотека
- **Vite** - быстрый сборщик
- **Tailwind CSS** - utility-first CSS
- **Recharts** - графики
- **Framer Motion** - анимации
- **Axios** - HTTP клиент

### DevOps
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy
- **Let's Encrypt** - SSL сертификаты
- **Ubuntu/Debian** - операционная система сервера

---

## 🚀 Быстрый старт (выберите свой вариант)

### Вариант 1: Локальная разработка
```bash
# Смотрите QUICKSTART.md
cd web/backend && python run.bat
cd web/frontend && npm run dev
```

### Вариант 2: Docker (локально)
```bash
cd web
docker-compose up -d
```

### Вариант 3: Production развертывание
```bash
# Смотрите DOCKER_DEPLOYMENT.md
# 1. Локально: сборка и push образов
# 2. На сервере: pull и запуск
# 3. Настройка Nginx + SSL
```

---

## ✅ Что выбрать?

| Задача | Документ | Описание |
|--------|----------|----------|
| 🔧 Разработка | [QUICKSTART.md](QUICKSTART.md) | Локальный запуск для разработки |
| 🐳 Развертывание | [INDEX_DOCKER.md](INDEX_DOCKER.md) | Навигация по Docker |
| 📖 Детали | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Полная инструкция |
| ⚡ Быстро | [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) | Для опытных |
| 📝 Команды | [COMMANDS.md](COMMANDS.md) | Справочник |
| 👤 Использование | [USER_GUIDE.md](USER_GUIDE.md) | Для пользователей |

---

## 🎯 Следующие шаги

### Если вы разработчик:
1. Прочитайте [README.md](README.md)
2. Запустите локально по [QUICKSTART.md](QUICKSTART.md)
3. Изучите API в [API_EXAMPLES.md](API_EXAMPLES.md)

### Если вы DevOps:
1. Откройте **[INDEX_DOCKER.md](INDEX_DOCKER.md)** для навигации
2. Изучите **[README_DOCKER.md](README_DOCKER.md)** для обзора
3. Следуйте **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** пошагово

### Если вы пользователь:
1. Откройте [USER_GUIDE.md](USER_GUIDE.md)
2. Перейдите на https://snee.companykd.world
3. Начните работу с системой

---

## 📞 Поддержка

### Нужна помощь?

- **Развертывание:** [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) → раздел "Решение проблем"
- **Команды:** [COMMANDS.md](COMMANDS.md) → поиск по Ctrl+F
- **Порты:** [PORTS_INFO.md](PORTS_INFO.md)
- **Скрипты:** [scripts/README.md](scripts/README.md)

---

## 🎉 Готово!

**Выберите свой путь и начинайте работу с SNЭЭ Graf!**

### Рекомендации:
- 👨‍💻 **Разработчик** → [README.md](README.md) → [QUICKSTART.md](QUICKSTART.md)
- 🚀 **DevOps** → **[INDEX_DOCKER.md](INDEX_DOCKER.md)** → **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)**
- 👤 **Пользователь** → [USER_GUIDE.md](USER_GUIDE.md)

---

**Создано с ❤️ для оптимизации энергетических систем**

*Версия: 1.0 | Дата: Декабрь 2024*

