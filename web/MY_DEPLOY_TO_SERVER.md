# Переходим на сервере с одной версии на другую
# 1# Переходим на 
cd /opt/snee-graf

# 2# Просматриваем запущенные контейнеры,
# смотрим версию 
docker-compose ps
docker images
docker image ls -a

# 3# останавливаем и удаляем контейнеры
docker-compose down

# 4# Для удаления образов с сервера меняем (контролируем) 
# версию в /opt/snee-graf/docker-compose.yml
Latest или 1.2

# 5# Удаляем только локальные образы, собранные самим compose:
docker-compose down --rmi local

# 10# Удалить образ
docker image rm end2040/snee_web_spes-backend:1.524
docker image rm end2040/snee_web_spes-frontend:1.524

# 6# меняем версию в /opt/snee-graf/docker-compose.yml
# для закачки (pull) с Docker Hub
Latest на 1.2

# 7# Качаем (pull) с Docker Hub. Контролируем версию закачки в 
docker-compose pull

# 8# Просматриваем список образов: 
docker images

# 9# Создаем контейнеры:
docker compose up -d

# 11# Просмотреть список образов в докер можно командой
docker image ls -a

# 12# Чтобы узнать количество доступного дискового пространства на облачном сервере, подключись по SSH и выполните команду 
df -h /

# 13# Удалить все остановленные контейнеры (если нужно):
docker container prune

# 14# Подключиться к облачному серверу вы можете по SSH по инструкции: rак подключиться через SSH 
https://reg.cloud/support/cloud/oblachnyye-servery/rabota-s-serverom/podklyucheniye-k-oblachnomu-serveru?utm_source=reg.ru&utm_medium=organic&utm_content=%2F&utm_campaign=reg.cloud#2
