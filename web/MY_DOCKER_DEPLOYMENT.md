#1 Переходим в папку web
cd "C:\den\Cursor\SNEE graf\web"

Собираем образы с использованием файлов в папке web: 
Dockerfile.backend.prod
Dockerfile.frontend.prod
# docker-compose.prod.yml
# nginx-server.conf
# .dockerignore
# backend/env.example.prod
# frontend/env.example.prod
# scripts/

#1 Запустить на компьютере  Docker Desktop

#2 Собираем Backend образ
docker build -f Dockerfile.backend.prod -t end2040/snee_web_spes-backend:1.520 .
# latest .

#3 Собираем Frontend образ
docker build -f Dockerfile.frontend.prod -t end2040/snee_web_spes-frontend:1.520 .
# latest .


## 🚀 Часть 2: Загрузка в Docker Hub

### 2.1. Вход в Docker Hub
docker login

Введите ваш username # и password от Docker Hub.

### 2.2. Push образов в Docker Hub
# Push Backend
docker push end2040/snee_web_spes-backend:1.520
# latest
# Push Frontend
docker push end2040/snee_web_spes-frontend:1.520
# latest
