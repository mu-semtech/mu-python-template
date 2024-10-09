#! /usr/bin/env bash
set -eu
if [ ${MODE:-""} == "development" ]; then 
    if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; fi
    exec gunicorn -k gthread --reload -c "$GUNICORN_CONF" "$APP_MODULE"
else 
    exec gunicorn -k gthread -c "$GUNICORN_CONF" "$APP_MODULE"
fi
