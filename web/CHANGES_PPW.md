# Список изменений - Добавление варианта PPW

## Новые файлы

### Backend
- `web/backend/quadratic_optimizer.py` - Модуль квадратичной оптимизации с alglib IPM
- `web/backend/ppw_calculator.py` - Калькулятор PPW с портированными алгоритмами из VB

### Frontend
- `web/frontend/src/components/DataInputSection_ppw.jsx` - Ввод данных для PPW
- `web/frontend/src/components/DataVisualizationSection_ppw.jsx` - Визуализация данных PPW
- `web/frontend/src/components/ChartsSection_ppw.jsx` - Графики результатов PPW
- `web/frontend/src/components/SchematicSection_ppw.jsx` - Схема энергопотоков PPW

### Документация
- `web/PPW_VARIANT_README.md` - Полное описание варианта PPW
- `web/IMPLEMENTATION_SUMMARY.md` - Итоги реализации
- `web/CHANGES_PPW.md` - Этот файл

## Измененные файлы

### Backend
- `web/backend/main.py`
  - Добавлен импорт `PPWCalculator`
  - Добавлены модели данных для PPW API
  - Добавлены эндпоинты `/api/v1/ppw/calculate-load` и `/api/v1/ppw/calculate-optimal-parameters`

### Frontend
- `web/frontend/src/App.jsx`
  - Добавлено состояние `activeVariant` для переключения вариантов
  - Добавлены состояния для PPW варианта с суффиксом `_ppw`
  - Добавлена функция `handleCalculate_ppw()`
  - Реализован условный рендеринг компонентов
  - Импорты новых PPW компонентов

- `web/frontend/src/components/Hero.jsx`
  - Добавлены props `activeVariant` и `setActiveVariant`
  - Добавлены стильные табы для переключения вариантов
  - Обновлена анимация с учетом новых элементов

- `web/frontend/src/services/api.js`
  - Добавлены методы `calculatePPWSchedule()` и `calculatePPWOptimalParameters()`

## Не реализовано (отложено на будущее)

1. **BatteryInteractiveSection_ppw** - Интерактивная SVG батарея
   - Сложная логика drag & resize
   - Требует отдельной итерации разработки

2. **Расширенные Tooltips** - Полные подсказки с терминологией ГОСТ
   - Базовые tooltips реализованы
   - Требуется расширение на все компоненты

3. **Тестирование** - Юнит-тесты и валидация
   - Требует настройки тестового окружения
   - Сравнение с VB версией

## Зависимости

### Существующие (используются)
- `web/alglib-cpython/` - Библиотека численной оптимизации (уже в проекте)

### Новых зависимостей не требуется
Все необходимые библиотеки уже установлены:
- Backend: FastAPI, numpy, pydantic
- Frontend: React, Recharts, Framer Motion, TailwindCSS

## Запуск проекта

### Backend
```bash
cd web/backend
python main.py
```

### Frontend
```bash
cd web/frontend
npm run dev
```

### Доступ
- Frontend: http://localhost:5173
- Backend API: http://localhost:8002
- API Docs: http://localhost:8002/docs

## Использование

1. Откройте веб-интерфейс
2. В Hero секции выберите "Вариант 2 (PPW)"
3. Загрузите профиль или используйте данные по умолчанию
4. Настройте параметры СНЭЭ
5. Нажмите "Рассчитать график"
6. Изучите результаты на графиках

## Особенности PPW варианта

### Отличия от Варианта 1
- **10 параметров** вместо 3
- **Разделение** входной и выходной мощности
- **Квадратичная оптимизация** вместо water-filling
- **Точное решение** с использованием IPM метода

### Приоритеты пересчета
1. Мощность (первый приоритет)
2. Энергия (второй приоритет)
3. Время и КПД (третий приоритет - автоматически)

### Цветовое кодирование
- Красный - входная мощность/заряд
- Зеленый - выходная мощность/разряд
- Желтый - КПД
- Фиолетовый - время

## Структура кода

### Backend API
```
POST /api/v1/ppw/calculate-load
Request: {
  system_load: [24 значения],
  rated_power_in_mw: float,
  rated_power_out_mw: float,
  capacity_mwh: float,
  efficiency: float
}
Response: {
  eess_energy_available: [24],
  eess_load: [24],
  resulting_balance: [24],
  soc: [24],
  summary: {...},
  system_load_deficit: float,
  system_load_reserve: float,
  termination_code: int
}
```

### Frontend Компоненты
```
App.jsx
├── Hero (с табами)
└── activeVariant === 'ppw' ?
    ├── DataInputSection_ppw
    ├── DataVisualizationSection_ppw
    ├── ChartsSection_ppw
    └── SchematicSection_ppw
```

## Известные ограничения

1. Интерактивная SVG батарея не реализована
2. Tooltips частично реализованы
3. Нет функции расчета оптимальных параметров в UI (API готов)
4. Экспорт результатов в Excel не реализован

## Дальнейшее развитие

См. раздел "Дальнейшее развитие" в `PPW_VARIANT_README.md`

## Техническая поддержка

При возникновении проблем:
1. Проверьте логи backend в консоли
2. Проверьте Network tab в DevTools браузера
3. Убедитесь, что alglib-cpython установлен корректно
4. Проверьте, что используются правильные порты (8002 для backend, 5173 для frontend)

---

**Версия**: 2.0.0-ppw  
**Дата**: 2025-12-12  
**Статус**: Готов к использованию

