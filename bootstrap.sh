#!/bin/sh
set -e

cd pdfding

if [ "$DATABASE_TYPE" = "POSTGRES" ]
then
    POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    echo "Waiting for postgres..."

    while ! nc -z postgres $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 core.wsgi:application