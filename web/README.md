# СНЭЭ Graf - Web Version

Современная веб-версия системы визуализации диспетчерского графика СНЭЭ с трендовым UI и интерактивными графиками.

## 🚀 Возможности

- **Современный UI/UX** с использованием Tailwind CSS и Framer Motion
- **Интерактивные графики** на базе Recharts
- **SVG визуализация** потоков энергии в реальном времени
- **Drag & Drop** загрузка Excel файлов
- **Редактирование данных** в визуальном режиме
- **Экспорт результатов** в Excel
- **Адаптивный дизайн** для всех устройств
- **REST API** на FastAPI

## 📁 Структура проекта

```
web/
├── backend/           # FastAPI сервер
│   ├── main.py       # Основной файл API
│   ├── requirements.txt
│   ├── run.bat       # Скрипт запуска (Windows)
│   └── env.example   # Пример конфигурации
│
├── frontend/         # React приложение
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   │   ├── Hero.jsx
│   │   │   ├── DataInputSection.jsx
│   │   │   ├── DataVisualizationSection.jsx
│   │   │   ├── ChartsSection.jsx
│   │   │   ├── SchematicSection.jsx
│   │   │   └── Footer.jsx
│   │   ├── services/      # API клиент
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
└── README.md         # Этот файл
```

## 🛠 Установка и запуск

### Backend (FastAPI)

1. Перейдите в директорию backend:
```bash
cd web/backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Запустите сервер:
```bash
# Windows
run.bat

# Linux/Mac
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

API будет доступен по адресу: http://localhost:8001
Документация: http://localhost:8001/docs

### Frontend (React)

1. Перейдите в директорию frontend:
```bash
cd web/frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите dev сервер:
```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3001

## 🎨 Технологии

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **Uvicorn** - ASGI сервер
- **Pydantic** - валидация данных
- **NumPy** - вычисления
- **Pandas** - обработка данных
- **OpenPyXL** - работа с Excel

### Frontend
- **React 18** - UI библиотека
- **Vite** - сборщик и dev сервер
- **Tailwind CSS** - utility-first CSS framework
- **Recharts** - библиотека графиков
- **D3.js** - визуализация данных
- **Framer Motion** - анимации
- **Lucide React** - иконки
- **Axios** - HTTP клиент
- **React Dropzone** - drag & drop файлов
- **XLSX** - работа с Excel в браузере

## 📦 Сборка для продакшена

### Backend

Для развертывания на сервере используйте:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

Или с использованием Gunicorn:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Frontend

1. Создайте production сборку:
```bash
npm run build
```

2. Файлы будут находиться в директории `dist/`

3. Разверните на любом статическом хостинге или используйте:
```bash
npm run preview
```

## 🌐 Развертывание на Reg.ru

### Вариант 1: Виртуальный хостинг

1. **Backend**: Загрузите файлы backend на сервер через FTP/SSH
2. Создайте файл `.env` на основе `env.example`
3. Установите зависимости: `pip install -r requirements.txt`
4. Настройте веб-сервер (nginx/Apache) для проксирования к FastAPI

### Вариант 2: VPS

1. Подключитесь к серверу по SSH
2. Клонируйте репозиторий
3. Установите зависимости для backend и frontend
4. Настройте Nginx как reverse proxy
5. Используйте systemd для автозапуска backend
6. Соберите frontend и разместите в `/var/www/`

Пример конфигурации Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.ru;

    # Frontend
    location / {
        root /var/www/snee-graf/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Вариант 3: Docker (рекомендуется)

См. `docker-compose.yml` в корне проекта для containerized развертывания.

## 📝 API Документация

После запуска backend, полная API документация доступна по адресам:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Основные эндпоинты:

- `GET /api/v1/health` - проверка работоспособности
- `GET /api/v1/default-profile` - профиль по умолчанию
- `POST /api/v1/calculate` - расчет графика СНЭЭ
- `POST /api/v1/upload-excel` - загрузка Excel файла
- `POST /api/v1/validate-profile` - валидация профиля

## 🎯 Секции лендинга

1. **Hero** - приветственная секция с анимацией
2. **Исходные данные** - загрузка и настройка параметров
3. **Визуализация данных** - графики исходного профиля
4. **Результаты расчета** - диспетчерский график и статистика
5. **Схема системы** - интерактивная SVG визуализация

## 🤝 Поддержка

Для вопросов и предложений создавайте issue в репозитории проекта.

## 📄 Лицензия

См. LICENSE файл в корне проекта.

