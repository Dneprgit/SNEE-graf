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
docker image rm end2040/snee_web_spes-backend:1.530
docker image rm end2040/snee_web_spes-frontend:1.530

# 6# меняем версию в /opt/snee-graf/docker-compose.yml
# для закачки (pull) с Docker Hub
Latest на 1.2

# 7# Качаем (pull) с Docker Hub. Контролируем версию закачки в 
docker-compose pull

# 8# Просматриваем список образов: 
docker images

# 9# Создаем контейнеры:
docker compose up -d

# HTML-задачи для страницы "Прочие задачи СПЭС"
# 9.1# Создаем каталог на сервере
mkdir -p /opt/snee-graf/html_task

# 9.2# Проверяем, 
релиз 1: что в /opt/snee-graf/backend/.env есть строка HTML_TASKS_DIR=/opt/snee-graf/html_task
релиз 2: .env не создавался, проверить в docker-composer.yml на сервере:
     HTML_TASKS_DIR=/opt/snee-graf/html_task
и
             volumes:
      - /opt/snee-graf/html_task:/opt/snee-graf/html_task:ro

# 9.3# После добавления новых html файлов в /opt/snee-graf/html_task
# backend должен видеть этот каталог через volume в docker-compose.yml

# 9.4# Перезапускаем backend контейнер после изменения .env или docker-compose.yml
docker compose up -d --force-recreate snee-backend-spes

# 9.5# После правки nginx-конфига не забываем перезагрузить nginx
sudo nginx -t && sudo systemctl reload nginx

# 11# Просмотреть список образов в докер можно командой
docker image ls -a

# 12# Чтобы узнать количество доступного дискового пространства на облачном сервере, подключись по SSH и выполните команду 
df -h /

# 13# Удалить все остановленные контейнеры (если нужно):
docker container prune

# 14# Подключиться к облачному серверу вы можете по SSH по инструкции: rак подключиться через SSH 
https://reg.cloud/support/cloud/oblachnyye-servery/rabota-s-serverom/podklyucheniye-k-oblachnomu-serveru?utm_source=reg.ru&utm_medium=organic&utm_content=%2F&utm_campaign=reg.cloud#2
