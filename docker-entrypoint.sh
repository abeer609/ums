#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate
python manage.py loaddata permissions.json
python manage.py loaddata role.json

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000