#!/bin/sh

python manage.py collectstatic --no-input               #copy static files into STATIC_ROOT
python manage.py migrate                                #create a new sqlite db inside the container
gunicorn slicedog.wsgi:application --bind 0.0.0.0:8000  #start the django application
