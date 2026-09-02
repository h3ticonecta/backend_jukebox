web: python manage.py migrate --noinput && python manage.py ensure_superuser && python manage.py ensure_bucket && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
