#! /usr/bin/env bash
set -eu
opts="${MODULE_NAME}:app --host 0.0.0.0 --port 80 --proxy-headers --timeout-keep-alive 300 --workers ${WEB_CONCURRENCY}"

if [ "${MODE}" == "development" ]; then 
    opts+=" --reload --reload-dir /app"
fi

exec uv run uvicorn $opts
