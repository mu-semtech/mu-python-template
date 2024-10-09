#! /usr/bin/env bash
set -eu

if [ ${MODE:-""} == "development" ]
then
    if [ -f /app/requirements.txt ]
    then
        pip install -r /app/requirements.txt
    fi
    exec gunicorn -k gthread --reload -c "/gunicorn_config.py" "web:app"
else 
    exec gunicorn -k gthread -c "/gunicorn_config.py" "web:app"
fi
