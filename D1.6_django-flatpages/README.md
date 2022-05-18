### D1.6. Финальный проект - Django flatpages

Версия Python 3.8.10  
Версия Django 4.0.4

Установка:
1. Создаем папку для проекта
2. Переносим в нее проект (project, env.txt)
3. Создаем виртуальное окружение из папки проекта в командной строке: virtualenv env
4. Активируем установленное виртуальное окружение: source env/bin/activate
5. Устанавливаем пакеты: pip install -r env.txt
6. Переходим в папку project и проверяем установку: python manage.py runserver

Сохранение установленных пакетов: pip freeze > env.txt

Параметры Django:
- usename:  admin
- password: admin

Flatpages:
- http://localhost:8000/start/
- http://localhost:8000/task/
- http://localhost:8000/italic/
- http://localhost:8000/double/
- http://localhost:8000/changes/
- http://localhost:8000/private/

