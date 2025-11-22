#!/bin/bash
set -e

echo "Starting Django application..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-localhost} ${REDIS_PORT:-6379}; do
  sleep 0.1
done
echo "Redis is ready!"

# Navigate to api directory
cd /app/api

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Initialize domains
echo "Initializing political domains..."
python manage.py init_domains || echo "Domains already initialized"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (only in development)
if [ "$DJANGO_DEBUG" = "True" ]; then
    echo "Creating superuser (if not exists)..."
    python manage.py shell << EOF
from db.entities.user_entity import User, UserProfile, UserSettings
import os

email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')

if not User.objects.filter(email=email).exists():
    user = User.objects.create(
        google_id='admin-google-id',
        email=email,
        username=username,
        is_admin=True
    )
    UserProfile.objects.create(user=user, display_name='Administrator')
    UserSettings.objects.create(user=user)
    print(f'Superuser {username} created successfully!')
else:
    print('Superuser already exists')
EOF
fi

echo "Starting application..."
exec "$@"

