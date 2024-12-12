# Интернет магазин
### Реализация бэкенд сервиса Интернет магазина 

В этом проекте раелизован Web API с использованием Django REST framework (в качестве базы данных используется PostgreSQL).

## Запуск проекта

Для развертывания проекта используется `Docker Compose`.

Чтобы запустить проект используем команду:
```
docker compose up -d
```

При первом запуске проекта создается база данных. 
Для заполнения её данными используем команду `loaddatautf8`:
```
docker compose exec app python manage.py loaddatautf8 fixtures/data.json
```
Стартовая страница проекта [http://127.0.0.1:8000](http://127.0.0.1:8000).

![Стартовая страница проекта](readmy/image_1.jpg)

В сервисе зарегистрировано 4 пользователя:
- суперпользователь admin (password: 01097);
- Sem, Tom, jhon (password: 1qaz!QAZ)


You can send HTTP requests from [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs).

## Licence

Author: Author: Stanislav Rubtsov