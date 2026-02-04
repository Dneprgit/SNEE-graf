# Переходим на сервере с одной версии на другую
# 1# Переходим на 
cd /opt/snee-graf

# 2# Просматриваем запущенные контейнеры,
# смотрим версию образов
docker-compose  ps

# 3# останавливаем и удаляем контейнеры
docker-compose down

# 4# Для удаления образов с сервера меняем (контролируем) 
# версию в /opt/snee-graf/docker-compose.yml
Latest или 1.2

# 5# Удаляем только локальные образы, собранные самим compose:
docker-compose down --rmi local

# 6# меняем версию в /opt/snee-graf/docker-compose.yml
# для закачки (pull) с Docker Hub
Latest на 1.2

# 7# Качаем (pull) с Docker Hub. Контролируем версию закачки в 
docker-compose pull

# 8# Просматриваем список образов: 
docker images

# 9# Создаем контейнеры:
docker compose up -d

# 10# 