release: cd products_api && python manage.py migrate
web: cd products_api && gunicorn products_api.wsgi --log-file -
celery: cd products_api && celery -A products_api worker -l info