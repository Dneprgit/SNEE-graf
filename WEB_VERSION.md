# 🌐 СНЭЭ Graf - Web Version

**Современная веб-версия системы визуализации диспетчерского графика работы системы накопления электрической энергии (СНЭЭ)**

## ✨ Особенности

### 🎨 Современный UI/UX
- **Трендовый дизайн** с использованием Tailwind CSS
- **Плавные анимации** на базе Framer Motion
- **Адаптивная верстка** для всех устройств
- **Градиентные фоны** и эффекты свечения
- **Интуитивная навигация** между секциями

### 📊 Интерактивная визуализация
- **Recharts графики** с зумом и tooltip
- **D3.js диаграммы** для сложных визуализаций
- **SVG схема системы** с анимацией потоков энергии
- **Редактирование данных** в реальном времени
- **Динамическое обновление** при изменении параметров

### 🔧 Функциональность
- **Drag & Drop** загрузка Excel файлов
- **Импорт/Экспорт** данных
- **Валидация входных данных**
- **Расчет оптимального графика** по алгоритму water-filling
- **Детальная статистика** эффективности СНЭЭ

### 🚀 Технологический стек

#### Backend
- **FastAPI** - Современный Python web framework
- **Uvicorn** - Быстрый ASGI сервер
- **NumPy** - Научные вычисления
- **Pandas** - Обработка данных
- **Pydantic** - Валидация данных

#### Frontend
- **React 18** - UI библиотека
- **Vite** - Быстрый сборщик
- **Tailwind CSS** - Utility-first CSS
- **Recharts** - Библиотека графиков
- **D3.js** - Визуализация данных
- **Framer Motion** - Анимации
- **Axios** - HTTP клиент

## 📁 Структура проекта

```
SNEE Graf/
├── web/                          # Веб-версия
│   ├── backend/                  # FastAPI сервер
│   │   ├── main.py              # API endpoints
│   │   ├── requirements.txt     # Python зависимости
│   │   ├── Dockerfile           # Docker образ backend
│   │   └── env.example          # Пример конфигурации
│   │
│   ├── frontend/                # React приложение
│   │   ├── src/
│   │   │   ├── components/     # React компоненты
│   │   │   │   ├── Hero.jsx                    # Приветственная секция
│   │   │   │   ├── DataInputSection.jsx        # Загрузка данных
│   │   │   │   ├── DataVisualizationSection.jsx # Визуализация профиля
│   │   │   │   ├── ChartsSection.jsx           # Графики результатов
│   │   │   │   ├── SchematicSection.jsx        # SVG схема
│   │   │   │   └── Footer.jsx                   # Футер
│   │   │   ├── services/       # API клиент
│   │   │   │   └── api.js
│   │   │   ├── App.jsx         # Главный компонент
│   │   │   ├── main.jsx        # Entry point
│   │   │   └── index.css       # Глобальные стили
│   │   ├── package.json        # Node.js зависимости
│   │   ├── vite.config.js      # Конфигурация Vite
│   │   ├── tailwind.config.js  # Конфигурация Tailwind
│   │   └── Dockerfile          # Docker образ frontend
│   │
│   ├── docker-compose.yml      # Docker Compose конфигурация
│   ├── nginx.conf              # Конфигурация Nginx
│   ├── start-dev.bat           # Автозапуск (Windows)
│   ├── start-dev.sh            # Автозапуск (Linux/Mac)
│   ├── README.md               # Документация
│   ├── QUICKSTART.md           # Быстрый старт
│   ├── DEPLOYMENT.md           # Развертывание
│   ├── TESTING.md              # Тестирование
│   └── API_EXAMPLES.md         # Примеры API
│
├── energy_storage_calculator.py # Модуль расчетов СНЭЭ
├── data_manager.py              # Управление данными
├── visualization.py             # Визуализация (PyQt6)
└── main_window.py               # Десктоп версия (PyQt6)
```

## 🚀 Быстрый старт

### Вариант 1: Автоматический запуск (рекомендуется)

#### Windows
```bash
cd web
start-dev.bat
```

#### Linux/Mac
```bash
cd web
chmod +x start-dev.sh
./start-dev.sh
```

### Вариант 2: Ручной запуск

#### Backend
```bash
cd web/backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

#### Frontend
```bash
cd web/frontend
npm install
npm run dev
```

### Вариант 3: Docker
```bash
cd web
docker-compose up -d
```

## 🌐 Доступ к приложению

После запуска:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [README.md](web/README.md) | Полная документация проекта |
| [QUICKSTART.md](web/QUICKSTART.md) | Быстрый старт для разработчиков |
| [DEPLOYMENT.md](web/DEPLOYMENT.md) | Развертывание на сервере Reg.ru |
| [TESTING.md](web/TESTING.md) | Руководство по тестированию |
| [API_EXAMPLES.md](web/API_EXAMPLES.md) | Примеры использования API |

## 🎯 Секции лендинга

### 1. Hero - Приветственная секция
- Анимированный заголовок с градиентом
- Плавающие фоновые элементы
- Карточки с ключевыми возможностями
- Индикатор прокрутки

### 2. Исходные данные
- **Drag & Drop загрузка** Excel файлов
- **Профиль по умолчанию** одной кнопкой
- **Скачивание шаблона** Excel
- **Настройка параметров** СНЭЭ:
  - Мощность инвертора (МВт)
  - Емкость батареи (МВтч)
  - КПД цикла

### 3. Визуализация исходных данных
- **Статистика профиля**: мин, макс, среднее, избытки, дефициты
- **Линейный график** суточного баланса
- **Столбчатая диаграмма** распределения
- **Таблица редактирования** с возможностью изменения каждого значения

### 4. Результаты расчета
- **Ключевые показатели**:
  - Покрытие дефицита (%)
  - Использование избытка (%)
  - Суммарные заряд/разряд
- **Диспетчерский график** с наложением:
  - Исходный баланс (область)
  - Заряд СНЭЭ (синие столбцы)
  - Разряд СНЭЭ (зеленые столбцы)
  - Результирующий баланс (черная линия)
- **График SOC** (состояние заряда батареи)
- **Экспорт результатов** в Excel

### 5. Схема системы (SVG)
- **Интерактивная схема** с компонентами:
  - Батарея с индикатором заряда
  - Инвертор
  - Электрическая сеть
- **Анимированные потоки энергии**:
  - Зеленые стрелки при разряде
  - Красные стрелки при заряде
- **Выбор часа слайдером** для анализа конкретного момента
- **Информационная панель** с текущими параметрами

## 🎨 Дизайн-система

### Цветовая палитра
- **Primary**: Оттенки синего (#0ea5e9)
- **Accent**: Оттенки фиолетового (#d946ef)
- **Success**: Зеленый (#10b981)
- **Warning**: Оранжевый (#f59e0b)
- **Danger**: Красный (#ef4444)

### Анимации
- Fade in/out эффекты
- Slide up появление секций
- Hover эффекты на кнопках
- Smooth scroll между секциями
- Пульсация индикаторов

## 🔌 API Endpoints

### `GET /api/v1/health`
Проверка работоспособности API

### `GET /api/v1/default-profile`
Получение профиля баланса по умолчанию

### `POST /api/v1/calculate`
Расчет диспетчерского графика СНЭЭ
- **Input**: load_profile (24 значения), параметры СНЭЭ
- **Output**: график работы, SOC, статистика

### `POST /api/v1/upload-excel`
Загрузка профиля из Excel файла
- **Input**: Excel файл (.xlsx, .xls)
- **Output**: массив из 24 значений

### `POST /api/v1/validate-profile`
Валидация профиля баланса
- **Input**: массив из 24 значений
- **Output**: статус валидации + статистика

## 🚀 Развертывание на Reg.ru

Подробные инструкции см. в [DEPLOYMENT.md](web/DEPLOYMENT.md)

### Быстрый гайд:

1. **Подключитесь к VPS по SSH**
2. **Установите необходимое ПО**: Python 3.11+, Node.js 18+, Nginx
3. **Клонируйте проект**: `git clone ...`
4. **Настройте Backend**: создайте venv, установите зависимости
5. **Настройте Systemd**: для автозапуска backend
6. **Соберите Frontend**: `npm run build`
7. **Настройте Nginx**: скопируйте конфигурацию
8. **Получите SSL**: используйте Let's Encrypt

## 🧪 Тестирование

```bash
# Тест backend API
curl http://localhost:8000/api/v1/health

# Тест расчета
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d @test_data.json

# Frontend dev сервер
cd web/frontend
npm run dev
```

Подробнее в [TESTING.md](web/TESTING.md)

## 📊 Производительность

- **Lighthouse Score**: 90+
- **Bundle Size**: ~500KB (gzipped)
- **API Response Time**: < 1s для расчетов
- **Initial Load**: < 2s на быстром соединении

## 🔒 Безопасность

- CORS настроен для конкретных доменов
- HTTPS с Let's Encrypt сертификатами
- Валидация всех входных данных
- Rate limiting на API (в продакшене)
- Защита от XSS и CSRF

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

См. LICENSE файл в корне проекта.

## 👨‍💻 Авторы

- Energy Storage Team

## 🙏 Благодарности

- FastAPI за отличный фреймворк
- Recharts за красивые графики
- Tailwind CSS за современный дизайн
- Framer Motion за плавные анимации

## 📞 Поддержка

- 📧 Email: info@example.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: См. документацию в папке `web/`

---

**Создано с ❤️ для оптимизации энергетических систем**

