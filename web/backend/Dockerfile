# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Копируем родительские модули (для импорта)
COPY ../../energy_storage_calculator.py /parent/
COPY ../../data_manager.py /parent/

# Добавляем родительскую директорию в PYTHONPATH
ENV PYTHONPATH=/parent:$PYTHONPATH

# Открываем порт
EXPOSE 8001

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

