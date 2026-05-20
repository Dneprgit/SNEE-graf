# Авторизация NotebookLM на сервере

Backend использует `notebooklm-py` и обращается к заранее подготовленному блокноту по ID. Новый блокнот из приложения не создается.

## Переменные окружения

Добавьте на сервере:

```bash
NOTEBOOKLM_NOTEBOOK_ID=your-notebook-id
NOTEBOOKLM_AUTH_JSON='{"cookies":[...]}'
```

`NOTEBOOKLM_NOTEBOOK_ID` - ID подготовленного блокнота NotebookLM с материалами FAQ по подаче исходных данных.

`NOTEBOOKLM_AUTH_JSON` - полный JSON из файла авторизации NotebookLM. По документации `notebooklm-py`, эта переменная имеет приоритет над файловым хранилищем и подходит для серверов/CI без браузера: [https://github.com/teng-lin/notebooklm-py/blob/main/docs/configuration.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/configuration.md)

## Как получить NOTEBOOKLM_AUTH_JSON

1. Установите `notebooklm-py` локально на компьютере, где доступен браузер:

```bash
pip install notebooklm-py
```

1. Выполните локальную авторизацию:

```bash
notebooklm login
```

1. Пройдите вход Google в открывшемся браузере.
2. Скопируйте все содержимое файла:

```bash
~/.notebooklm/profiles/default/storage_state.json
```

Для старых версий библиотеки путь может быть:

```bash
~/.notebooklm/storage_state.json
```

Содержимое должно начинаться с `{"cookies":[...]}`.

1. Передайте этот JSON в переменную окружения `NOTEBOOKLM_AUTH_JSON` на сервере.

## Пример для Linux-сервера

```bash
export NOTEBOOKLM_NOTEBOOK_ID="your-notebook-id"
export NOTEBOOKLM_AUTH_JSON='{"cookies":[...]}'
```

Если переменные задаются в env-файле, JSON лучше держать одной строкой.

## Пример для PowerShell

```powershell
$env:NOTEBOOKLM_NOTEBOOK_ID = "your-notebook-id"
$env:NOTEBOOKLM_AUTH_JSON = '{"cookies":[...]}'
```

## Проверка

После установки зависимостей и настройки переменных запустите backend и отправьте POST-запрос:

```bash
curl -X POST http://localhost:8002/api/v1/input-data-faq/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Какие исходные данные нужны для расчета?"}'
```

Ожидаемый ответ:

```json
{
  "answer": "..."
}
```

Если сессия истекла, повторите `notebooklm login` локально и обновите `NOTEBOOKLM_AUTH_JSON` на сервере.