# СНЭЭ Graf

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-frontend-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-dev%20server-646cff.svg)](https://vitejs.dev/)
![License](https://img.shields.io/badge/License-Educational-orange.svg)

## О проекте

`СНЭЭ Graf` - это актуальная web-версия системы расчета и визуализации диспетчерского графика для систем накопления электрической энергии.

Проект состоит из:
- `FastAPI` backend с API для расчета графика, подбора параметров СНЭЭ, загрузки Excel и публикации HTML-задач.
- `React + Vite` frontend с интерактивным интерфейсом редактирования профиля, сравнением решателей и визуализацией результатов.

Актуальная версия проекта ориентирована на QP/LP-оптимизацию.

## Актуальные решатели

В backend реализованы и используются следующие варианты расчета диспетчерского графика:

1. `SciPy linprog (HiGHS)`  
   Базовый расчет через линейную постановку задачи. Доступен через endpoint `POST /api/v1/calculate-qp`.

2. `HiGHS QP (highspy)`  
   Реальная квадратичная оптимизация на базе `highspy`. Доступен через `POST /api/v1/calculate-qp-highs`.

3. `HiGHS QP modified`  
   Модифицированный QP-решатель, учитывающий `standby_load_mw` и влияние собственных нужд на баланс и эквивалентный КПД. Доступен через `POST /api/v1/calculate-qp-highs-modified`.

Кроме расчета графика, backend поддерживает отдельный расчет оценочных параметров СНЭЭ через `POST /api/v1/calculate-optimal-parameters-qp`.

## Что умеет система

- расчет диспетчерского графика СНЭЭ по суточному профилю из 24 точек;
- загрузка баланса мощности из Excel и выдача Excel-шаблона;
- ручное редактирование всех 24 значений профиля;
- интерактивное редактирование графика перетаскиванием точек;
- пакетная вставка данных из Excel прямо в поля;
- сдвиг всего профиля и плавное изменение соседних точек;
- расчет оценочных параметров СНЭЭ;
- переключение между заводскими и оценочными параметрами;
- запуск расчета разными решателями из одного интерфейса;
- отображение ключевых KPI, SOC, результирующего баланса и потоков энергии;
- экспорт результатов в Excel;
- отображение дополнительных HTML-инструментов на отдельной странице.

## Актуальный интерфейс

### Основной экран `СНЭЭ Graf`

Во frontend сейчас реализован не просто статический лендинг, а полноценный расчетный интерфейс:

- верхняя навигация между основной страницей и страницей `Прочие задачи СПЭС`;
- hero-блок продукта;
- секция загрузки и редактирования исходного профиля;
- визуальный редактор профиля с drag-and-drop корректировкой точек;
- переключатели debug-режима для QP-расчетов;
- блок расчета оценочных параметров;
- интерактивный SVG-блок настройки батареи;
- запуск диспетчерского графика тремя разными решателями;
- графики результатов, SOC и экспорт в Excel;
- интерактивная схема потоков энергии по выбранному часу.

### Страница `Прочие задачи СПЭС`

Во frontend добавлена отдельная страница с автоматическим каталогом HTML-задач:

- backend формирует манифест HTML-файлов;
- frontend показывает карточки задач с названием и автором;
- выбранная HTML-страница открывается встроенно через `iframe`;
- задачу можно открыть и в отдельной вкладке.

Это позволяет использовать проект как единую web-точку входа не только для расчета СНЭЭ, но и для дополнительных прикладных HTML-инструментов.

## Архитектура

```text
SNEE graf/
├── web/
│   ├── backend/                 FastAPI API и вычислительная логика
│   ├── frontend/                React/Vite интерфейс
│   ├── run-backend.bat          локальный запуск backend
│   ├── run-frontend.bat         локальный запуск frontend
│   └── README.md                расширенная документация web-версии
└── .github/README.md            GitHub-описание репозитория
```

## Локальный запуск

Для локального запуска используйте bat-скрипты из каталога `web`.

1. Перейдите в каталог проекта:

```bat
cd web
```

2. Запустите backend:

```bat
run-backend.bat
```

Скрипт:
- создает `venv`, если окружение еще не создано;
- активирует виртуальное окружение;
- устанавливает Python-зависимости;
- запускает FastAPI на `http://localhost:8002`.

3. В отдельном терминале запустите frontend:

```bat
run-frontend.bat
```

Скрипт:
- устанавливает npm-зависимости при необходимости;
- запускает Vite dev server на `http://localhost:3002`.

### Локальные адреса

- Frontend: `http://localhost:3002`
- Backend API: `http://localhost:8002`
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Основные API endpoints

- `GET /api/v1/health` - проверка состояния backend
- `GET /api/v1/default-profile` - профиль по умолчанию
- `GET /api/v1/html-tasks` - каталог HTML-задач
- `POST /api/v1/upload-excel` - загрузка баланса из Excel
- `POST /api/v1/validate-profile` - валидация профиля
- `POST /api/v1/calculate-qp` - расчет графика через SciPy linprog
- `POST /api/v1/calculate-qp-highs` - расчет графика через HiGHS QP
- `POST /api/v1/calculate-qp-highs-modified` - расчет графика через модифицированный HiGHS QP
- `POST /api/v1/calculate-optimal-parameters-qp` - расчет оценочных параметров СНЭЭ

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

- [`../web/README.md`](../web/README.md) - основное описание web-версии
- [`../web/QUICKSTART.md`](../web/QUICKSTART.md) - быстрый старт
- [`../web/API_EXAMPLES.md`](../web/API_EXAMPLES.md) - примеры API
- [`../web/TESTING.md`](../web/TESTING.md) - тестирование
- [`../web/README_DOCKER.md`](../web/README_DOCKER.md) - Docker-описание
- [`../web/DOCKER_DEPLOYMENT.md`](../web/DOCKER_DEPLOYMENT.md) - развертывание

## Статус

- продукт развивается как web-платформа;
- основной расчетный сценарий построен вокруг QP/LP-решателей;
- frontend уже включает расширенный интерфейс настройки, анализа и визуализации;
- backend обслуживает как расчет СНЭЭ, так и каталог вспомогательных HTML-инструментов.

