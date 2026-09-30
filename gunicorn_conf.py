# Gunicorn configuration for the mu-python-template.
# Origin: defaults of the deprecated base image `tiangolo/meinheld-gunicorn`
# (docker-images/gunicorn_conf.py, MIT), simplified to what the template uses
# and documents.

import os

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)

# Gunicorn config variables
loglevel = os.getenv("LOG_LEVEL", "info")
workers = max(1, int(os.getenv("WEB_CONCURRENCY", "1")))
bind = bind_env if bind_env else "{host}:{port}".format(host=host, port=port)
keepalive = 120  # Value used by the base image this template was historically based on
errorlog = "-"
