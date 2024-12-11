#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    # если база еще не запущена
    echo "DB not yet run..."
    # Проверяем доступность хоста и порта
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "DB did run."
fi
# Удаляем все старые данные
python manage.py flush --no-input
# Выполняем миграции
python manage.py migrate
# Сбор статистических файлов
python manage.py collectstatic --no-input --clear
#python manage.py runserver 0.0.0.0:8000
gunicorn online_shop.wsgi:application --bind 0.0.0.0:8000
exec "$@"
