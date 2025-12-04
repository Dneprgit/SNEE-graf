# Распространение EXE файла

## 📦 Готовый к распространению пакет

### Содержимое папки `dist/`

```
dist/
├── SNEE_Graf.exe     # Исполняемый файл (~220 МБ)
├── .env              # Файл конфигурации
└── README.txt        # Краткая инструкция
```

## 🚀 Способы распространения

### Вариант 1: Прямая передача папки

1. Скопируйте всю папку `dist/` пользователю
2. Пользователь запускает `SNEE_Graf.exe`
3. Файл `.env` должен быть в той же папке!

### Вариант 2: ZIP архив

```bash
# Создайте архив:
Compress-Archive -Path dist\* -DestinationPath SNEE_Graf_v1.0.1.zip

# Или используйте любой архиватор (7-Zip, WinRAR и т.д.)
```

Инструкция для пользователя:
1. Распаковать архив в любую папку
2. Запустить `SNEE_Graf.exe`

### Вариант 3: Installer (опционально)

Можно создать установщик с помощью:
- **Inno Setup** (рекомендуется)
- **NSIS**
- **Advanced Installer**

## 📋 Требования для пользователя

### Минимальные

- **ОС:** Windows 10/11 (64-bit)
- **RAM:** 2 GB свободной памяти
- **Место на диске:** ~250 MB

### Дополнительные

- Microsoft Visual C++ Redistributable (обычно уже установлен)
- Windows Defender отключен или добавлено исключение

## ⚠️ Важные замечания

### 1. Файл .env обязателен

EXE файл ищет файл `.env` в той же папке. Если его нет, программа использует встроенные значения, но лучше его включить.

### 2. Антивирусы

Антивирусы могут ложно срабатывать на PyInstaller EXE файлы. Решения:

**Для разработчика:**
- Подписать EXE цифровой подписью
- Загрузить на VirusTotal для анализа
- Создать белый список у популярных антивирусов

**Для пользователя:**
- Добавить `SNEE_Graf.exe` в исключения антивируса
- Временно отключить защиту при первом запуске
- Скачать с проверенного источника (GitHub Releases)

### 3. Первый запуск

- Может занять 2-5 секунд (распаковка)
- Последующие запуски быстрее (~1 секунда)

### 4. Права администратора

Обычно не требуются, но если возникают проблемы:
- Запустить от имени администратора
- Переместить в папку без ограничений (не Program Files)

## 📊 Размер файлов

```
SNEE_Graf.exe:  ~220 МБ (229,959,129 байт)
.env:           <1 КБ
README.txt:     <1 КБ
───────────────────────────────────────
Всего:          ~220 МБ
```

Большой размер обусловлен включением:
- Python runtime
- PyQt6 библиотеки
- Chromium (для отображения графиков)
- NumPy, Pandas, Plotly
- Все зависимости

## 🌐 Публикация на GitHub Releases

### Создание релиза

```bash
# 1. Создать архив
Compress-Archive -Path dist\* -DestinationPath SNEE_Graf_v1.0.1.zip

# 2. Создать tag
git tag -a v1.0.1 -m "Release version 1.0.1"

# 3. Push tag
git push origin v1.0.1

# 4. На GitHub:
#    - Перейти в Releases
#    - Создать новый Release
#    - Прикрепить SNEE_Graf_v1.0.1.zip
#    - Добавить Release Notes
```

### Release Notes (пример)

```markdown
## СНЭЭ - Визуализация диспетчерского графика v1.0.1

### 🎉 Основные возможности
- Расчет оптимального диспетчерского графика СНЭЭ
- Интерактивная визуализация (Plotly)
- Импорт/экспорт Excel
- Настраиваемые параметры

### 📦 Установка
1. Скачать `SNEE_Graf_v1.0.1.zip`
2. Распаковать в любую папку
3. Запустить `SNEE_Graf.exe`

### ⚙️ Системные требования
- Windows 10/11 (64-bit)
- 2 GB RAM
- 250 MB свободного места

### 🐛 Исправления
- Добавлена зависимость PyQt6-WebEngine
- Обновлена документация

### 📝 Документация
- [README.md](https://github.com/Dneprgit/SNEE-graf/blob/main/README.md)
- [QUICKSTART.md](https://github.com/Dneprgit/SNEE-graf/blob/main/QUICKSTART.md)
```

## 🔒 Безопасность

### Цифровая подпись (рекомендуется)

Для профессионального распространения:

1. Получить код подписи (Code Signing Certificate)
2. Подписать EXE:
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\SNEE_Graf.exe
   ```
3. Проверить:
   ```bash
   signtool verify /pa dist\SNEE_Graf.exe
   ```

### Контрольная сумма

```bash
# SHA256
certutil -hashfile dist\SNEE_Graf.exe SHA256

# Опубликовать в Release Notes для проверки целостности
```

## 📄 Лицензия и копирайт

Добавьте файл LICENSE в dist/:
```bash
copy LICENSE dist\LICENSE.txt
```

## 🎯 Чеклист перед публикацией

- [ ] EXE файл работает на чистой системе
- [ ] .env файл включен
- [ ] README.txt с инструкциями
- [ ] Антивирус не блокирует (или есть инструкция)
- [ ] Протестировано на Windows 10 и 11
- [ ] Создан архив
- [ ] Создан Git tag
- [ ] Release Notes готовы
- [ ] (Опционально) Цифровая подпись
- [ ] (Опционально) Контрольная сумма

## 📞 Поддержка пользователей

### Частые вопросы

**Q: Антивирус блокирует**  
A: Добавьте в исключения или скачайте с официального репозитория

**Q: Не запускается**  
A: Проверьте, что .env файл рядом с EXE

**Q: Медленно работает**  
A: Первый запуск всегда медленнее, закройте другие приложения

**Q: Нужен ли Python?**  
A: Нет, Python уже встроен в EXE

### Обратная связь

Пользователи могут сообщать о проблемах:
- GitHub Issues: https://github.com/Dneprgit/SNEE-graf/issues
- Email: указать контакты

## 🚀 Автоматизация (CI/CD)

В будущем можно настроить GitHub Actions для автоматической сборки:

```yaml
# .github/workflows/build.yml
name: Build EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pyinstaller SNEE_Graf.spec
      - uses: actions/upload-artifact@v2
        with:
          name: SNEE_Graf
          path: dist/SNEE_Graf.exe
```

---

**Готово к распространению! 🎉**

Для вопросов см. [README.md](README.md) или создайте [Issue](https://github.com/Dneprgit/SNEE-graf/issues)

