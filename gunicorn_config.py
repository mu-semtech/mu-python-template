import os

loglevel = os.getenv("LOG_LEVEL", "info")
workers = int(os.getenv("WORKERS", "4"))
bind = "0.0.0.0:80"
errorlog = os.getenv("ERROR_LOG", "-")
worker_tmp_dir = "/dev/shm"
accesslog = os.getenv("ACCESS_LOG", "-")
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "120"))
timeout = int(os.getenv("TIMEOUT", "120"))
keepalive = int(os.getenv("KEEP_ALIVE", "5"))
