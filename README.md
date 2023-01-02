# Simple social network app (backend only)
Social network app where user can:
  - add/remove friends
  - create/update/delete posts
  - comment posts
  - like/dislike posts
  - chat with friends
  
Tech stack:
  - Django
  - Django Rest Framework
  - Pytest
  - Channels
  - Redis
  - SQLite (optionally can be changed on PostgreSQL or MongoDB)
  
Installation:
  - clone rep ```git clone https://github.com/SaviolaX/Simple_social_network```
  - ```cd Simple_social_network``` and create env ```python -m venv env```, activate one ```env/Scripts/activate```(Windows)
  - install dependencies ```pip install -r requirements.txt```
  - create superuser ```python manage.py createsuperuser```
  - run dev server ```python manage.py runserver```
  
Run test:
  in terminal ```pytest``` or ```pytest -s``` - to see error details
