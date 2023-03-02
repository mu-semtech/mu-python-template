#! /usr/bin/env bash
set -eu
if [ ${MODE:-""} == "development" ]; then 
    exec python web.py
else 
    exec gunicorn -k egg:meinheld#gunicorn_worker -c "$GUNICORN_CONF" "$APP_MODULE"
fi
