#! /usr/bin/env bash
set -eu
opts="${MODULE_NAME}:app --host 0.0.0.0 --port 80 --proxy-headers --timeout-keep-alive 300 --workers ${WEB_CONCURRENCY}"

if [ "${MODE}" == "development" ]; then 
    if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; fi
    opts+=" --reload"
fi

exec uvicorn $opts
