#!/bin/sh
set -e

echo "Running migrations..."
uv run python manage.py migrate

echo "Creating superuser..."
uv run python manage.py shell -c "
from apps.users.infrastructure.models import CustomUser
if not CustomUser.objects.filter(email='admin@admin.com').exists():
    CustomUser.objects.create_superuser(email='admin@admin.com', password='admin123', first_name='Admin', last_name='User')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "Starting server..."
exec uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000
