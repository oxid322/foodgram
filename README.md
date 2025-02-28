<h1>Приложение рецептов Foodgram</h1>

Запуск приложения производится из папки ```foodgram/infra```

Создайте файл ```.env``` в главной директории проекта
Пример:
```
POSTGRES_USER=djangouser
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY='pivo'
```

Для запуска требуется Docker

Из папки ```foodgram/infra``` выполните ```docker compose up --build``` - запуск всех контейнеров из папки

<a>http://localhost/</a> Сайт приложения

<a>http://localhost/admin/</a> панель администрирования

Для создания супер пользователя необходимо выполнить команду:

```docker exec -it foodgram-back  python manage.py createsuperuser```

Только с правами суперпользователя можно будет зайти в админ панель
