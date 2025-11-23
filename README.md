# City Library --- система перераспределения книг

Проект моделирует сеть городских библиотек. Каждая книга существует в
единственном экземпляре, а каждая библиотека имеет ограниченную
вместимость. Система позволяет:

1.  Загрузить данные (авторы, книги, библиотеки)
2.  Выполнить первичное размещение книг
3.  Перераспределить книги равномерно, учитывая capacity

## 1. Клонирование репозитория

``` bash
git clone https://github.com/<your_username>/city_library.git
cd city_library
```

## 2. Создание виртуального окружения и установка зависимостей

``` bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate        # Windows
```

Установка зависимостей:

``` bash
pip install -r requirements.txt
```

## 3. Применить миграции

``` bash
python manage.py migrate
```

## 4. Загрузить исходные данные

``` bash
python manage.py load_initial_data
```

Источник данных: `library/data/initial_data.json`

## 5. Первичное распределение книг

``` bash
python manage.py init_inventory
```

## 6. Перераспределение книг

``` bash
python manage.py rebalance_libraries
```
