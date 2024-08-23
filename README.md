<h1 align="center" style="border-bottom: solid 2px;">Проект Foodgram</h1>
<h3 align="center">
    <a href="https://myfoodgram.zapto.org">Адрес сайта</a>
</h3>
<h5 style="border-bottom: solid 1px;">Данные для входа (admin user): email --- danil680068@yandex.ru, password --- 1</h5>

<h2 align="center">Стек технологий</h2>

<p align="center">
    <a href="https://www.djangoproject.com/">
        <img alt="Django" src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white">
    </a>
    <a href="https://www.django-rest-framework.org/">
        <img alt="Django-REST-Framework" src="https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray">
    </a>
    <a href="https://www.postgresql.org/">
        <img alt="PostgreSQL" src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white">
    </a>
    <a href="https://nginx.org/ru/">
        <img alt="Nginx" src="https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white">
    </a>
    <a href="https://gunicorn.org/">
        <img alt="gunicorn" src="https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white">
    </a>
    <a href="https://www.docker.com/">
        <img alt="docker" src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white">
    </a>
</p>
<h2 align="center">Описание</h2>

<p>
    Foodgram - приложение, с помощью которого, пользователи могут создавать рецепты, добавлять в избраное, создавать список покупок и подписываться на авторов рецептов.</p>
    <h2>Основные возможности</h2>
    <ul>
        <li>Регистрация пользователей и авторизация по токену</li>
        <li>CRUD-операции с рецептами (создание, обновление, удаление, получение рецептов)</li>
        <li>Добавление рецептов в избранное и в корзину покупок</li>
        <li>Подписка на пользователей и просмотр их рецептов</li>
        <li>Фильтрация рецептов по тегам, автору, избранному и корзине покупок</li>
        <li>Скачивание списка покупок</li>
    </ul>
</p>

<h3 align="center">
    <a href="https://myfoodgram.zapto.org">Пример сайта</a><p></p>

</h3>

<h2 align="center">Запуск</h2>

```shell
# Склонировать репозиторий
git clone git@github.com:DanilKhmyrov/foodgram.git
```

> [!IMPORTANT]
> Необходимо создать файл `.env` с переменными окружения в папке `infra`.</br>
> Пример файла
> POSTGRES_DB=
> POSTGRES_USER=
> POSTGRES_PASSWORD=
> DB_HOST=
> DB_PORT=

```shell
# Запустить docker compose
# Необходимо находится в директории infra/
docker compose up -d
```

## Как наполнить БД данными

```bash
# Добавить ингредиенты
# Необходимо находится в директории infra/
docker compose exec backend python manage.py load_data .
```
