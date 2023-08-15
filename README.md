# YaTube
## Социальная сеть YaTube - сеть для публикации постов пользователей, с возможностью подписки на понравившихся авторов.

В проекте реализованы следующие функции:

+ добавление/удаление постов авторизованными пользователями
+ редактирование постов только его автором
+ возможность авторизованным пользователям оставлять комментарии к постам
+ подписка/отписка на понравившихся авторов
+ создание отдельной ленты с постами авторов, на которых подписан пользователь
+ создание отдельной ленты постов по группам(тематикам)
Подключены пагинация, кеширование, авторизация пользователя, возможна смена пароля через почту. Неавторизованному пользователю доступно только чтение. Покрытие тестами.

## Технологии:
+ Python 3.7
+ Django 2.2.16
+ Unittest
+ Bootstrap

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/EvgenyMi/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
