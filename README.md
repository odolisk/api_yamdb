# API YamDB

## Проект Django REST API.

### Требования

- Указаны в **requirements.txt**

### Запуск проекта в dev-mode

- Установите и активируйте виртуальное окружение venv. [Подробнее](https://pythoner.name/documentation/tutorial/venv)
- Установите зависимости из **requirements.txt**

```python
pip install -r requirements.txt
```

- Запустите миграции (из папки с manage.py)

```python
python manage.py migrate
```

- Создайте суперпользователя:

```python
 python manage.py createsuperuser
```

- Запустите сервер

```python
 python manage.py runserver 
```

Документация доступна по адресу http://Localhost:8000/redoc/