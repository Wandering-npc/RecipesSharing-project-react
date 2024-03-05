# RecipesSharing

"RecipesSharing" -  это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также  доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Сайт выполнен на основе django rest framework и react

Сайт доступен по адресу http://myhost.servebeer.com/

Админ: a@a.ru Пароль: отныне не знаю

# Для локального запуска проекта:
 
1. Склонируйте репозиторий 

```bash
git clone git@github.com:Wandering-npc/RecipesSharing-project-react.git
```

2. Создайте в корне проекта .env файл (пример файла указан в репозитории)

3. Выполните команды:
```bash
docker compose up
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/ 
docker compose exec backend python manage.py load_csv
```

Запущенный проект будет доступен по адресу http://localhost/

### Некоторые примеры API запросов:
* ```/api/users/{id}``` GET-запрос. Страница пользователя с указанным id (доступно неавторизованным).
* ```/api/users/me/``` GET-запрос. Страница авторизованого пользователя. Доступно авторизированным пользователям.
* ```/api/users/{id}/subscribe/``` POST-запрос. Подписка на выбраного по id пользователя. Доступно авторизированным пользователям.
* ```/api/users/subscriptions/``` GET-запрос. Получить список всех авторов, на которых подписан текущий юзер. Доступно авторизированным пользователям.
* ```/api/tags/``` GET-запрос. Получение списка тегов. (доступно неавторизованным)
* ```/api/ingredients/``` GET-запрос. Получение списка ингредиентов. (доступно неавторизованным)
* ```/api/recipes/``` GET-запрос. Получение всех рецептов. (доступно неавторизованным). POST-запрос. Добавить новый рецепт (Доступно авторизированным пользователям).
* ```/api/recipes/download_shopping_cart/``` GET-запрос. Получить файл со списком необходимых для блюд ингредиентов. Доступно авторизированным пользователям.
* ```/api/auth/token/login/``` POST-запрос. Получить токен авторизации. 
