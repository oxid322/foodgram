<h1>Приложение рецептов Foodgram</h1>

Запуск приложения производится из папки ```foodgram/infra```

Для запуска необходим Docker

Из папки ```foodgram/infra``` выполните ```docker compose up --build``` - запуск всех контейнеров из папки

<a>http://localhost/</a> Сайт приложения

<a>http://localhost/admin/</a> панель администрирования

Для создания супер пользователя необходимо выполнить команду:

```docker exec -it foodgram-back  python manage.py createsuperuser```

Только после этого можно будет зайти в админ панель
