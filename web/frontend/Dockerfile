# Используем Node.js образ
FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package файлы
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы
COPY . .

# Открываем порт
EXPOSE 3002

# Команда запуска для разработки
CMD ["npm", "run", "dev", "--", "--host"]

# Для продакшена используйте:
# RUN npm run build
# CMD ["npm", "run", "preview", "--", "--host"]

