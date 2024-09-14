#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start Daphne
echo "Starting Daphne..."
daphne -b 0.0.0.0 -p 8000 config.asgi:application
