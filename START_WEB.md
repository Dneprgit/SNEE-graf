# 🚀 Быстрый запуск Web версии

## Вариант 1: Автоматический запуск (самый простой)

### Windows
```bash
cd web
start-dev.bat
```

### Linux/Mac
```bash
cd web
chmod +x start-dev.sh
./start-dev.sh
```

Откроются два окна терминала:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

## Вариант 2: Docker (если установлен Docker)

```bash
cd web
docker-compose up -d
```

## После запуска

Откройте браузер и перейдите на:
```
http://localhost:3000
```

## Что дальше?

1. Нажмите **"Профиль по умолчанию"**
2. Нажмите **"Рассчитать график"**
3. Изучите результаты!

## Документация

Полная документация в папке `web/`:
- [README.md](web/README.md) - Полное описание
- [QUICKSTART.md](web/QUICKSTART.md) - Быстрый старт
- [USER_GUIDE.md](web/USER_GUIDE.md) - Руководство пользователя
- [DEPLOYMENT.md](web/DEPLOYMENT.md) - Развертывание на сервере
- [WEB_VERSION.md](WEB_VERSION.md) - Обзор веб-версии

## Возникли проблемы?

См. раздел "Возможные проблемы" в [QUICKSTART.md](web/QUICKSTART.md)

