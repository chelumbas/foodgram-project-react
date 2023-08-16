# Foodgram

## Описание
Социальная сеть для обмена рецептами.

## Установка

В примерах описана установка на Ubuntu Linux.

# Запуск
Docker необходим для запуска сервиса, так как компоненты сервиса работают в контейнерах.
Docker Image собраны для архитектуры AMD64.
В примерах приведена установка и запуск на Linux Ubuntu.

## Установка Docker
- Перейти в терминале под пользователя root.
```sudo -i```
- Обновить списки пакетов ОС.
```apt update```
- Установить пакет curl.
```apt install curl```
- Скачать сценарий get-docker.sh.
```curl -fSL https://get.docker.com -o get-docker.sh```
- Запустить сценарий.
```sh ./get-docker.sh```
- Установить docker-compose-plugin
```apt install docker-compose-plugin```

## Подготовка Docker Compose и переменных окружений
docker-compose.yml это файл содержащий инструкции, для запуска и настройки сервисов.

- Перейти в директорию с docker-compose файлами, либо создать новую.
- Скопировать docker-compose.production.yml из репозитория, либо создать собственный файл.
- Создать в директории файл `.env` с секретами для переменных окружений.
Необходимые переменные:
```
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DB_HOST=
DB_PORT=
```
## Запуск в Docker
- Запустить Docker Compose в режиме демона.
```docker compose -f docker-compose.production.yml up -d ```
- Выполнить подготовку миграции, собрать статические файлы бэкенда.
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /static/
```

## Настройка работы с NGINX (Опционально. Если на сервере уже установлен.)
Необходимо перенаправить запросы в Docker
- Изменить конфиг ```/etc/nginx/sites-enabled/default```
Пример рабочего файла:
```
server {
        server_name server_name <IP адрес сервера> <доменное имя>;
        
        location /media/ {
                proxy_pass http://localhost-ip:port;
        }
        
        location /api/ {
                proxy_pass http://localhost-ip:port;
        }

        location /admin/ {
                proxy_pass http://localhost-ip:port;
        }

        location / {
                proxy_pass http://localhost-ip:port;
        }
```
- Проверить, что конфигурация составлена верно.
```nginx -t```
- Перезапустить Nginx.
```systemctl reload nginx```

# Для ревью
- Адрес: 158.160.12.45 / ya-foodgram.ddns.net
- Логин: admin
- Пароль: Ckj;ysqGfhjkm78!