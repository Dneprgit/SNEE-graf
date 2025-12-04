# Ветки Git

## Структура веток

### 📌 main
- **Назначение:** Основная стабильная ветка
- **Статус:** Stable
- **Защита:** Только через Pull Request
- **Описание:** Содержит стабильную версию кода, готовую к релизу

### 🔧 dev1
- **Назначение:** Ветка разработки
- **Статус:** Development
- **Описание:** Активная разработка новых функций и исправлений

## Текущее состояние

```bash
$ git branch -a
* dev1                    # Текущая ветка
  main                    # Основная ветка
  remotes/origin/dev1     # Удаленная dev1
  remotes/origin/main     # Удаленная main
```

## Рабочий процесс

### Для разработчиков

1. **Работа с dev1:**
   ```bash
   git checkout dev1
   # ... внесите изменения ...
   git add .
   git commit -m "Описание изменений"
   git push origin dev1
   ```

2. **Создание Pull Request:**
   - После завершения функции
   - Из dev1 в main
   - С описанием изменений

3. **Синхронизация с main:**
   ```bash
   git checkout dev1
   git pull origin main
   git push origin dev1
   ```

### Для администраторов

1. **Merge dev1 → main:**
   ```bash
   git checkout main
   git merge dev1
   git push origin main
   ```

2. **Создание релиза:**
   ```bash
   git tag -a v1.0.1 -m "Release 1.0.1"
   git push origin v1.0.1
   ```

## История коммитов

### Последний коммит
```
6dac73f dev1
```

**Содержимое:** Полный проект СНЭЭ v1.0.1
- Все исходные файлы
- Документация
- Конфигурация
- Тесты

## Правила работы

### ✅ Можно
- Коммитить в dev1 напрямую
- Создавать feature-ветки от dev1
- Делать Pull Request в main

### ❌ Нельзя
- Коммитить в main напрямую (только через PR)
- Удалять ветки без согласования
- Force push в main

## Создание новых веток

### Feature-ветка
```bash
git checkout dev1
git checkout -b feature/название-функции
# ... работа ...
git push -u origin feature/название-функции
```

### Bugfix-ветка
```bash
git checkout dev1
git checkout -b bugfix/описание-ошибки
# ... исправление ...
git push -u origin bugfix/описание-ошибки
```

### Hotfix-ветка (для срочных исправлений в main)
```bash
git checkout main
git checkout -b hotfix/критическая-ошибка
# ... исправление ...
git push -u origin hotfix/критическая-ошибка
# После проверки: merge в main И в dev1
```

## Синхронизация

### Обновление локальной копии
```bash
git fetch origin
git status
```

### Просмотр изменений
```bash
git log origin/dev1..dev1       # Локальные коммиты не в remote
git log dev1..origin/dev1       # Remote коммиты не в локале
```

## GitHub Actions (планируется)

В будущем можно настроить автоматизацию:
- [ ] Автоматические тесты при Push
- [ ] Проверка стиля кода (pylint, black)
- [ ] Автоматическая сборка EXE
- [ ] Публикация релизов

## Ссылки

- **Репозиторий:** https://github.com/Dneprgit/SNEE-graf
- **Ветка dev1:** https://github.com/Dneprgit/SNEE-graf/tree/dev1
- **Ветка main:** https://github.com/Dneprgit/SNEE-graf/tree/main

---

**Обновлено:** Декабрь 2025

