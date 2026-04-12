# СНЭЭ Graf - Web Platform

`СНЭЭ Graf` - это актуальная web-платформа для расчета и визуализации диспетчерского графика систем накопления электрической энергии.

Проект состоит из `FastAPI` backend и `React + Vite` frontend. Backend выполняет расчеты, подбор параметров СНЭЭ, загрузку Excel и публикацию HTML-задач, а frontend предоставляет интерфейс редактирования профиля, запуска расчета разными решателями и анализа результатов.

## Возможности

- расчет диспетчерского графика СНЭЭ по 24-часовому профилю;
- загрузка баланса мощности из Excel и скачивание Excel-шаблона;
- ручное редактирование всех 24 значений профиля;
- вставка диапазонов значений из Excel прямо в поля ввода;
- интерактивное изменение профиля перетаскиванием точек;
- сдвиг всего профиля и плавное изменение соседних точек;
- расчет оценочных параметров СНЭЭ;
- переключение между заводскими и оценочными параметрами;
- запуск расчета тремя решателями из одного интерфейса;
- отображение KPI, SOC, результирующего баланса и потоков энергии;
- экспорт результатов в Excel;
- отдельная страница `Прочие задачи СПЭС` с HTML-инструментами.

## Актуальные решатели

В backend доступны следующие варианты расчета диспетчерского графика:

1. `SciPy linprog (HiGHS)`  
   Линейная постановка задачи. Endpoint: `POST /api/v1/calculate-qp`

2. `HiGHS QP (highspy)`  
   Квадратичная оптимизация на базе `highspy`. Endpoint: `POST /api/v1/calculate-qp-highs`

3. `HiGHS QP modified`  
   Модифицированный QP-решатель с учетом `standby_load_mw` и влияния собственных нужд. Endpoint: `POST /api/v1/calculate-qp-highs-modified`

Для оценки параметров СНЭЭ используется отдельный endpoint `POST /api/v1/calculate-optimal-parameters-qp`.

## Актуальный интерфейс

### Основной экран `СНЭЭ Graf`

Во frontend сейчас реализован полноценный расчетный интерфейс, который включает:

- верхнюю навигацию между основной страницей и страницей HTML-задач;
- hero-блок продукта;
- секцию загрузки и редактирования профиля;
- визуальный редактор профиля с drag-and-drop корректировкой точек;
- debug-режим для QP-расчетов;
- блок расчета оценочных параметров;
- интерактивную SVG-настройку батареи;
- запуск диспетчерского графика тремя решателями;
- графики результатов, SOC и экспорт в Excel;
- интерактивную схему потоков энергии по выбранному часу.

### Страница `Прочие задачи СПЭС`

Во frontend добавлена отдельная страница с автоматическим каталогом HTML-задач:

- backend формирует манифест HTML-файлов;
- frontend показывает карточки задач с названием и автором;
- выбранная HTML-страница открывается встроенно через `iframe`;
- задачу можно открыть в отдельной вкладке.

## Структура проекта

```text
web/
├── run-backend.bat          локальный запуск backend
├── run-frontend.bat         локальный запуск frontend
├── backend/                 FastAPI API и вычислительная логика
│   ├── main.py
│   ├── graph.py
│   ├── energy_storage_calculator_.py
│   ├── data_manager.py
│   ├── requirements.txt
│   └── env.example
├── frontend/                React/Vite интерфейс
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── env.example
└── README.md
```

## Установка и запуск

### Локальный запуск

Для локального запуска используйте bat-скрипты из директории `web`.

1. Откройте терминал в директории `web`:

```bat
cd web
```

2. Запустите backend:

```bat
run-backend.bat
```

3. В отдельном терминале запустите frontend:

```bat
run-frontend.bat
```

`run-backend.bat` автоматически:

- создает `venv`, если окружение еще не создано;
- активирует виртуальное окружение;
- устанавливает Python-зависимости;
- запускает FastAPI.

`run-frontend.bat` автоматически:

- устанавливает npm-зависимости при необходимости;
- запускает Vite dev server.

### Локальные адреса

- Frontend: `http://localhost:3002`
- Backend API: `http://localhost:8002`
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

### Docker

Для серверного и production-развертывания используйте Docker.

Быстрый старт:

```bash
cd web
docker-compose up -d
```

Production-вариант:

```bash
cd web
docker-compose -f docker-compose.prod.yml up -d
```

Подробности смотрите в `README_DOCKER.md` и `DOCKER_DEPLOYMENT.md`.

## Технологии

### Backend

- `FastAPI`
- `Uvicorn`
- `Pydantic`
- `NumPy`
- `SciPy`
- `highspy`
- `Pandas`
- `OpenPyXL`
- `python-dotenv`

### Frontend

- `React 18`
- `Vite`
- `Tailwind CSS`
- `Framer Motion`
- `Recharts`
- `D3`
- `Lucide React`
- `Axios`
- `React Dropzone`
- `XLSX`

## API

После запуска backend документация доступна по адресам:

- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

Основные endpoints:

- `GET /api/v1/health`
- `GET /api/v1/default-profile`
- `GET /api/v1/html-tasks`
- `POST /api/v1/upload-excel`
- `POST /api/v1/validate-profile`
- `POST /api/v1/calculate-qp`
- `POST /api/v1/calculate-qp-highs`
- `POST /api/v1/calculate-qp-highs-modified`
- `POST /api/v1/calculate-optimal-parameters-qp`

## Сборка и deployment

### Backend

Пример запуска backend без bat-скрипта:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --workers 4
```

### Frontend

Production-сборка frontend:

```bash
npm run build
```

Предпросмотр production-сборки:

```bash
npm run preview
```

Пример `nginx` для reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.ru;

    location / {
        root /var/www/snee-graf/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Дополнительная документация

### Основная

- [`QUICKSTART.md`](QUICKSTART.md) - быстрый старт
- [`API_EXAMPLES.md`](API_EXAMPLES.md) - примеры API
- [`TESTING.md`](TESTING.md) - тестирование
- [`USER_GUIDE.md`](USER_GUIDE.md) - руководство пользователя

### По QP-логике и backend

- [`backend/QP_IMPLEMENTATION.md`](backend/QP_IMPLEMENTATION.md) - детали реализации QP
- [`backend/QP_ALGORITHM_README.md`](backend/QP_ALGORITHM_README.md) - описание алгоритма
- [`backend/QP_VALIDATION_CHECKLIST.md`](backend/QP_VALIDATION_CHECKLIST.md) - чеклист валидации

### Docker и развертывание

- [`README_DOCKER.md`](README_DOCKER.md) - обзор Docker-развертывания
- [`DOCKER_DEPLOYMENT.md`](DOCKER_DEPLOYMENT.md) - пошаговое развертывание
- [`QUICKSTART_DOCKER.md`](QUICKSTART_DOCKER.md) - быстрый старт Docker
- [`DEPLOYMENT.md`](DEPLOYMENT.md) - ручное развертывание
- [`scripts/README.md`](scripts/README.md) - скрипты автоматизации

## Статус

- проект развивается как web-платформа;
- основной пользовательский сценарий построен вокруг QP/LP-решателей;
- frontend уже включает расширенный интерфейс настройки, анализа и визуализации;
- backend обслуживает как расчеты СНЭЭ, так и каталог HTML-инструментов.

