from os import environ

bind = "0.0.0.0:" + environ.get("APP_PORT", "5000")
max_requests = 1000
workers = int(environ.get("APP_WORKERS", 1))
