# Multi-stage build для Frontend
# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Копирование package files
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Build приложения
ARG VITE_API_URL=http://localhost:8002
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: Production with nginx
FROM nginx:alpine

# Копирование nginx конфигурации
COPY nginx.conf /etc/nginx/nginx.conf

# Копирование билда из предыдущего stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1

# Expose порт
EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]
