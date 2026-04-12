# СНЭЭ Graf

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-frontend-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-dev%20server-646cff.svg)](https://vitejs.dev/)
![License](https://img.shields.io/badge/License-Educational-orange.svg)

## О проекте

`СНЭЭ Graf` - это web-платформа для расчета и визуализации диспетчерского графика систем накопления электрической энергии.

Текущая версия проекта построена вокруг `FastAPI` backend и `React + Vite` frontend. Backend отвечает за вычисления, подбор параметров СНЭЭ, загрузку Excel и публикацию HTML-задач, а frontend предоставляет интерактивный интерфейс для редактирования профиля, сравнения решателей и анализа результатов.

## Актуальные решатели

В backend сейчас доступны три основных варианта расчета диспетчерского графика:

1. `SciPy linprog (HiGHS)` через `POST /api/v1/calculate-qp`
2. `HiGHS QP (highspy)` через `POST /api/v1/calculate-qp-highs`
3. `HiGHS QP modified` через `POST /api/v1/calculate-qp-highs-modified`

Модифицированный вариант учитывает `standby_load_mw` и влияние собственных нужд на баланс и эквивалентный КПД.

Для оценки параметров СНЭЭ используется отдельный endpoint `POST /api/v1/calculate-optimal-parameters-qp`.

## Возможности

- расчет диспетчерского графика СНЭЭ по суточному профилю из 24 точек;
- загрузка баланса мощности из Excel и скачивание Excel-шаблона;
- ручное редактирование профиля и вставка значений из Excel;
- интерактивное изменение графика перетаскиванием точек;
- сдвиг профиля и плавное изменение соседних точек;
- расчет оценочных параметров СНЭЭ;
- переключение между заводскими и оценочными параметрами;
- запуск расчета разными решателями из одного интерфейса;
- отображение KPI, результирующего баланса, SOC и потоков энергии;
- экспорт результатов в Excel;
- отдельная страница `Прочие задачи СПЭС` с HTML-инструментами.

## Актуальный интерфейс

Основной экран `СНЭЭ Graf` включает:

- верхнюю навигацию между основной страницей и страницей HTML-задач;
- секцию загрузки и редактирования профиля;
- визуальный редактор профиля;
- debug-режим для QP-расчетов;
- блок расчета оценочных параметров;
- интерактивную настройку батареи;
- запуск расчета тремя решателями;
- графики результатов, SOC и экспорт в Excel;
- интерактивную схему потоков энергии по выбранному часу.

Дополнительно во frontend реализована страница `Прочие задачи СПЭС`, где backend автоматически публикует HTML-файлы, а frontend показывает их в виде карточек и открывает встроенно через `iframe`.

## Структура проекта

```text
SNEE graf/
├── web/
│   ├── backend/                 FastAPI API и вычислительная логика
│   ├── frontend/                React/Vite интерфейс
│   ├── run-backend.bat          локальный запуск backend
│   ├── run-frontend.bat         локальный запуск frontend
│   └── README.md                расширенная документация web-версии
├── .github/README.md            GitHub-описание
└── README.md                    корневой README репозитория
```

## Локальный запуск

Для локального запуска используйте bat-скрипты из каталога `web`.

1. Перейдите в каталог `web`:

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

Скрипт `run-backend.bat` автоматически создает `venv`, активирует окружение, устанавливает Python-зависимости и запускает FastAPI.

Скрипт `run-frontend.bat` автоматически устанавливает npm-зависимости и запускает Vite dev server.

### Локальные адреса

- Frontend: `http://localhost:3002`
- Backend API: `http://localhost:8002`
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Основные API endpoints

- `GET /api/v1/health`
- `GET /api/v1/default-profile`
- `GET /api/v1/html-tasks`
- `POST /api/v1/upload-excel`
- `POST /api/v1/validate-profile`
- `POST /api/v1/calculate-qp`
- `POST /api/v1/calculate-qp-highs`
- `POST /api/v1/calculate-qp-highs-modified`
- `POST /api/v1/calculate-optimal-parameters-qp`

## Технологии

### Backend

- `FastAPI`
- `Uvicorn`
- `NumPy`
- `SciPy`
- `highspy`
- `Pandas`
- `OpenPyXL`
- `python-dotenv`

### Frontend

- `React`
- `Vite`
- `Tailwind CSS`
- `Framer Motion`
- `Recharts`
- `Axios`
- `React Dropzone`
- `XLSX`

## Документация

- [`web/README.md`](web/README.md) - основное описание web-версии
- [`web/QUICKSTART.md`](web/QUICKSTART.md) - быстрый старт
- [`web/API_EXAMPLES.md`](web/API_EXAMPLES.md) - примеры API
- [`web/TESTING.md`](web/TESTING.md) - тестирование
- [`web/README_DOCKER.md`](web/README_DOCKER.md) - Docker
- [`web/DOCKER_DEPLOYMENT.md`](web/DOCKER_DEPLOYMENT.md) - развертывание

## Статус

- проект развивается как web-платформа;
- основной расчетный сценарий построен вокруг QP/LP-решателей;
- frontend уже включает расширенный интерфейс настройки и анализа;
- backend обслуживает как расчеты СНЭЭ, так и каталог HTML-инструментов.
