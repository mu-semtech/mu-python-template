#! /usr/bin/env bash
set -eu
if [ "${MODE}" == "development" ]; then
    if [ -f /app/requirements.txt ]; then uv pip install --system -r /app/requirements.txt; fi
    if [ "${DEV_SERVER:-flask}" == "gunicorn" ]; then
        exec gunicorn --reload -k gunicorn_worker.UvicornWSGIWorker -c /gunicorn_conf.py web:app
    else
        exec flask --app web.py run --debug --port 80 --host "0.0.0.0"
    fi
else
    exec gunicorn -k gunicorn_worker.UvicornWSGIWorker -c /gunicorn_conf.py web:app
fi
