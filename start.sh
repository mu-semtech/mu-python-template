#! /usr/bin/env bash
set -eu
if [ "${MODE}" == "development" ]; then
    if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; fi
    exec flask --app web.py run --debug --port 80 --host "0.0.0.0"
else
    exec gunicorn -k gunicorn_worker.UvicornWSGIWorker -c /gunicorn_conf.py web:app
fi
