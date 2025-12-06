# 📁 Обзор проекта СНЭЭ Graf

Комплексное решение для визуализации и расчета диспетчерского графика работы системы накопления электрической энергии (СНЭЭ).

## 🎯 Две версии приложения

### 1. Desktop версия (PyQt6)
Полнофункциональное настольное приложение с GUI

**Файлы**:
- `main.py` - точка входа
- `main_window.py` - главное окно приложения
- `energy_storage_calculator.py` - расчетный модуль
- `data_manager.py` - импорт/экспорт данных
- `visualization.py` - генерация графиков Plotly
- `example_data.py` - примеры данных

**Запуск**: `run.bat` или `python main.py`

**Компиляция**: `build.bat` → `dist/SNEE_Graf.exe`

### 2. Web версия (FastAPI + React)
Современное веб-приложение с трендовым UI

**Структура**: `web/`
- `backend/` - FastAPI REST API
- `frontend/` - React SPA
- Полная документация (7 файлов)
- Docker конфигурация
- Nginx конфигурация

**Запуск**: `web/start-dev.bat` или `web/start-dev.sh`

**Доступ**: http://localhost:3000

---

## 📂 Полная структура проекта

```
SNEE-Graf/
│
├── 🖥️ DESKTOP VERSION
│   ├── main.py                           # Точка входа
│   ├── main_window.py                    # GUI (PyQt6)
│   ├── energy_storage_calculator.py      # Расчетный движок
│   ├── data_manager.py                   # Управление данными
│   ├── visualization.py                  # Графики (Plotly)
│   ├── example_data.py                   # Примеры
│   ├── test_calculator.py                # Тесты
│   ├── run.bat                           # Запуск (Windows)
│   ├── build.bat                         # Компиляция в EXE
│   ├── SNEE_Graf.spec                    # PyInstaller спецификация
│   ├── requirements.txt                  # Python зависимости
│   ├── env.example                       # Пример конфигурации
│   └── dist/                             # Скомпилированный EXE
│       └── SNEE_Graf.exe
│
├── 🌐 WEB VERSION
│   └── web/
│       ├── 🔧 BACKEND (FastAPI)
│       │   ├── main.py                   # API endpoints
│       │   ├── requirements.txt          # Python зависимости
│       │   ├── Dockerfile                # Docker образ
│       │   ├── run.bat                   # Запуск (Windows)
│       │   ├── env.example               # Конфигурация
│       │   └── README.md                 # Backend документация
│       │
│       ├── 🎨 FRONTEND (React)
│       │   ├── src/
│       │   │   ├── components/           # React компоненты (6 шт)
│       │   │   │   ├── Hero.jsx
│       │   │   │   ├── DataInputSection.jsx
│       │   │   │   ├── DataVisualizationSection.jsx
│       │   │   │   ├── ChartsSection.jsx
│       │   │   │   ├── SchematicSection.jsx
│       │   │   │   └── Footer.jsx
│       │   │   ├── services/
│       │   │   │   └── api.js            # API клиент
│       │   │   ├── App.jsx               # Главный компонент
│       │   │   ├── main.jsx              # Entry point
│       │   │   └── index.css             # Глобальные стили
│       │   ├── package.json              # Node зависимости
│       │   ├── vite.config.js            # Vite конфиг
│       │   ├── tailwind.config.js        # Tailwind конфиг
│       │   ├── postcss.config.js         # PostCSS конфиг
│       │   ├── index.html                # HTML шаблон
│       │   ├── Dockerfile                # Docker образ
│       │   └── env.example               # Конфигурация
│       │
│       ├── 🐳 INFRASTRUCTURE
│       │   ├── docker-compose.yml        # Docker Compose
│       │   ├── nginx.conf                # Nginx конфигурация
│       │   ├── start-dev.bat             # Автозапуск (Windows)
│       │   └── start-dev.sh              # Автозапуск (Linux/Mac)
│       │
│       └── 📚 DOCUMENTATION
│           ├── README.md                 # Полная документация
│           ├── QUICKSTART.md             # Быстрый старт
│           ├── DEPLOYMENT.md             # Развертывание на Reg.ru
│           ├── TESTING.md                # Тестирование
│           ├── API_EXAMPLES.md           # Примеры API
│           ├── USER_GUIDE.md             # Руководство пользователя
│           └── SUMMARY.md                # Краткое описание
│
├── 📖 PROJECT DOCUMENTATION
│   ├── README.md                         # Главная документация
│   ├── CHANGELOG.md                      # История изменений
│   ├── VERSION.md                        # Версия и фичи
│   ├── INDEX.md                          # Навигация по документам
│   ├── PROJECT_STRUCTURE.md              # Структура проекта
│   ├── DEVELOPER.md                      # Для разработчиков
│   ├── QUICKSTART.md                     # Быстрый старт (desktop)
│   ├── INSTALL.md                        # Установка
│   ├── DISTRIBUTION.md                   # Распространение EXE
│   ├── BRANCHES.md                       # Git ветки
│   ├── NOTES.md                          # Заметки разработчика
│   ├── WEB_VERSION.md                    # Обзор веб-версии
│   ├── START_WEB.md                      # Быстрый запуск веб
│   └── PROJECT_OVERVIEW.md               # Этот файл
│
└── 🔧 CONFIGURATION
    ├── .gitignore                        # Git ignore
    ├── env.example                       # Конфигурация (desktop)
    └── web/.gitignore                    # Git ignore (web)
```

---

## 📊 Статистика проекта

### Desktop версия
- **Файлов кода**: 7 Python файлов
- **Строк кода**: ~1500+
- **Зависимостей**: 8 (NumPy, Pandas, PyQt6, Plotly, etc.)
- **Размер EXE**: ~220 МБ (включая Python runtime)
- **Документации**: 12 файлов

### Web версия
- **Backend**: 1 файл (~300 строк)
- **Frontend**: 9 файлов (~2000+ строк)
- **Компонентов**: 6 React компонентов
- **API endpoints**: 5
- **Зависимостей**: 
  - Backend: 8 Python пакетов
  - Frontend: 12 npm пакетов
- **Документации**: 7 файлов
- **Bundle size**: ~500 KB (gzipped)

### Общее
- **Всего файлов**: ~40+
- **Строк кода**: ~3500+
- **Строк документации**: ~3000+
- **Документов**: 20+ файлов

---

## 🚀 Быстрый старт

### Desktop версия
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск
run.bat
# или
python main.py

# Компиляция в EXE
build.bat
```

### Web версия
```bash
cd web

# Автоматический запуск
start-dev.bat           # Windows
./start-dev.sh          # Linux/Mac

# Или через Docker
docker-compose up -d

# Доступ
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 📚 Ключевые документы

### Для пользователей
1. **[README.md](README.md)** - Начните здесь
2. **[QUICKSTART.md](QUICKSTART.md)** - Desktop быстрый старт
3. **[START_WEB.md](START_WEB.md)** - Web быстрый старт
4. **[web/USER_GUIDE.md](web/USER_GUIDE.md)** - Руководство пользователя Web

### Для разработчиков
1. **[DEVELOPER.md](DEVELOPER.md)** - Руководство разработчика
2. **[web/README.md](web/README.md)** - Web документация
3. **[web/API_EXAMPLES.md](web/API_EXAMPLES.md)** - Примеры API
4. **[CHANGELOG.md](CHANGELOG.md)** - История изменений

### Для развертывания
1. **[DISTRIBUTION.md](DISTRIBUTION.md)** - Распространение Desktop
2. **[web/DEPLOYMENT.md](web/DEPLOYMENT.md)** - Развертывание Web на Reg.ru
3. **[web/TESTING.md](web/TESTING.md)** - Тестирование

### Обзорные
1. **[VERSION.md](VERSION.md)** - Версия и возможности
2. **[WEB_VERSION.md](WEB_VERSION.md)** - Обзор Web версии
3. **[web/SUMMARY.md](web/SUMMARY.md)** - Краткое описание Web
4. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Этот файл

---

## 🎯 Основные возможности

### Общие для обеих версий
- ✅ Расчет оптимального графика работы СНЭЭ (алгоритм water-filling)
- ✅ Импорт/экспорт данных в Excel
- ✅ Интерактивная визуализация результатов
- ✅ Настройка параметров (мощность, емкость, КПД)
- ✅ Детальная статистика эффективности
- ✅ Профиль баланса по умолчанию для демонстрации

### Desktop специфичные
- ✅ Нативное GUI на PyQt6
- ✅ Графики Plotly с зумом и панорамированием
- ✅ Сохранение графиков в HTML
- ✅ Компиляция в standalone EXE
- ✅ Работает без интернета

### Web специфичные
- ✅ Современный трендовый UI (Tailwind CSS)
- ✅ Плавные анимации (Framer Motion)
- ✅ Drag & Drop загрузка файлов
- ✅ Интерактивная SVG схема системы с анимацией потоков
- ✅ Редактирование данных в реальном времени
- ✅ REST API для интеграции
- ✅ Адаптивный дизайн (mobile-friendly)
- ✅ Доступ из любого места через браузер

---

## 🛠️ Технологии

### Desktop
- **Python 3.11+**
- **PyQt6** - GUI framework
- **NumPy** - вычисления
- **Pandas** - обработка данных
- **Plotly** - визуализация
- **PyInstaller** - компиляция в EXE

### Web Backend
- **FastAPI** - веб-фреймворк
- **Uvicorn** - ASGI сервер
- **NumPy** - вычисления
- **Pandas** - обработка данных
- **Pydantic** - валидация

### Web Frontend
- **React 18** - UI библиотека
- **Vite** - сборщик
- **Tailwind CSS** - стили
- **Recharts** - графики
- **D3.js** - визуализация
- **Framer Motion** - анимации
- **Axios** - HTTP клиент

### Infrastructure
- **Docker** - контейнеризация
- **Nginx** - веб-сервер
- **Systemd** - автозапуск

---

## 🌟 Что выбрать?

### Desktop версия если нужно:
- 🖥️ Работать без интернета
- 💾 Standalone приложение (один EXE файл)
- 🔒 Локальная обработка данных
- 🖱️ Традиционный desktop интерфейс
- 📦 Простое распространение (отправить EXE файл)

### Web версия если нужно:
- 🌐 Доступ из любого места
- 📱 Работа на мобильных устройствах
- 👥 Мультипользовательский доступ
- 🔗 Интеграция с другими системами через API
- 🎨 Современный трендовый UI
- ☁️ Централизованное развертывание на сервере
- 🔄 Автоматические обновления

---

## 📈 Дорожная карта

### Desktop версия
- ✅ v1.0.0 - Первый релиз
- ✅ v1.0.1 - EXE компиляция
- ✅ v2.0.0 - Web версия
- 🔜 v2.1.0 - Unit тесты
- 🔜 v2.2.0 - Темная тема
- 🔜 v3.0.0 - Мультипрофильный режим

### Web версия
- ✅ v2.0.0 - Первая версия
- 🔜 v2.1.0 - Аутентификация
- 🔜 v2.2.0 - База данных (история расчетов)
- 🔜 v2.3.0 - Сравнение вариантов
- 🔜 v2.4.0 - Расширенная аналитика
- 🔜 v3.0.0 - Real-time режим (WebSockets)

---

## 🤝 Вклад в проект

Приветствуются любые улучшения:
1. Fork репозиторий
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Откройте Pull Request

---

## 📞 Контакты

- 📧 Email: info@example.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: См. папку с документацией

---

## 📄 Лицензия

См. LICENSE файл в корне проекта

---

## 🙏 Благодарности

- NumPy и Pandas за мощные инструменты работы с данными
- PyQt6 за кроссплатформенный GUI
- Plotly за красивые интерактивные графики
- FastAPI за современный веб-фреймворк
- React за гибкую UI библиотеку
- Tailwind CSS за utility-first подход
- Framer Motion за плавные анимации
- Recharts и D3.js за визуализацию данных

---

**Создано с ❤️ для оптимизации энергетических систем**

**Версия проекта**: 2.0.0  
**Дата обновления**: Декабрь 2025  
**Статус**: ✅ Production Ready

