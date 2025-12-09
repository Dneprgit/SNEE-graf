# 🚀 Быстрый старт СНЭЭ Graf Web

Это краткое руководство для быстрого запуска веб-версии СНЭЭ Graf на локальной машине.

## Предварительные требования

- Python 3.11 или выше
- Node.js 18 или выше
- npm или yarn

## Автоматический запуск (рекомендуется)

### Windows

Просто запустите:
```bash
start-dev.bat
```

Это откроет два окна терминала:
- Backend (FastAPI) на http://localhost:8001
- Frontend (React) на http://localhost:3001

### Linux/Mac

```bash
chmod +x start-dev.sh
./start-dev.sh
```

Это создаст tmux сессию с тремя окнами для backend, frontend и команд.

## Ручной запуск

### 1. Запуск Backend

```bash
cd backend

# Создайте виртуальное окружение (только первый раз)
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
#source venv/bin/activate

# Установите зависимости (только первый раз)
pip install -r requirements.txt

# Запустите сервер
python -m uvicorn main:app --reload --port 8001

```

Backend будет доступен на: http://localhost:8001
API документация: http://localhost:8001/docs

### 2. Запуск Frontend

Откройте новый терминал:

```bash
cd frontend

# Установите зависимости (только первый раз)
npm install

# Запустите dev сервер
npm run dev
```

Frontend будет доступен на: http://localhost:3001

## 🎉 Готово!

Откройте браузер и перейдите на http://localhost:3001

## Что дальше?

1. **Загрузите данные**: Используйте drag & drop или кнопку "Профиль по умолчанию"
2. **Настройте параметры**: Введите параметры СНЭЭ (мощность, емкость, КПД)
3. **Рассчитайте график**: Нажмите кнопку "Рассчитать график"
4. **Исследуйте результаты**: Прокрутите вниз для просмотра графиков и SVG схемы

## Возможные проблемы

### Backend не запускается

**Ошибка**: `Module not found`

**Решение**: Убедитесь, что вы в правильной директории и активировали venv:
```bash
cd web/backend
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

### Frontend не запускается

**Ошибка**: `npm: command not found`

**Решение**: Установите Node.js с https://nodejs.org/

**Ошибка**: `EADDRINUSE: port 3001 already in use`

**Решение**: Порт занят. Либо остановите другое приложение, либо измените порт:
```bash
npm run dev -- --port 3002
```

### API запросы не работают

**Проблема**: Frontend не может подключиться к backend

**Решение**: 
1. Убедитесь, что backend запущен на порту 8001
2. Проверьте консоль браузера (F12) на наличие CORS ошибок
3. Проверьте файл `frontend/vite.config.js` - должен быть настроен proxy

## Структура проекта

```
web/
├── backend/              # FastAPI сервер
│   ├── main.py          # API endpoints
│   └── requirements.txt # Python зависимости
│
├── frontend/            # React приложение
│   ├── src/
│   │   ├── components/  # React компоненты
│   │   └── services/    # API клиент
│   └── package.json     # Node.js зависимости
│
├── start-dev.bat        # Автозапуск (Windows)
├── start-dev.sh         # Автозапуск (Linux/Mac)
└── README.md            # Полная документация
```

## Полезные команды

### Backend
```bash
# Проверка работоспособности
curl http://localhost:8001/api/v1/health

# Тестирование API
curl -X POST http://localhost:8001/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

### Frontend
```bash
# Сборка для продакшена
npm run build

# Предпросмотр production сборки
npm run preview

# Проверка на ошибки
npm run lint
```

## Горячие клавиши в tmux (Linux/Mac)

- `Ctrl+B` затем `0/1/2` - переключение между окнами
- `Ctrl+B` затем `D` - отсоединиться от сессии (серверы продолжат работу)
- `tmux attach -t snee-graf` - подключиться обратно
- `tmux kill-session -t snee-graf` - завершить все процессы

## Дополнительная документация

- [README.md](./README.md) - Полная документация
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Развертывание на сервере
- [backend/README.md](./backend/README.md) - API документация

## Поддержка

Если возникли проблемы:
1. Проверьте эту документацию
2. Посмотрите логи в терминале
3. Создайте issue в репозитории проекта

