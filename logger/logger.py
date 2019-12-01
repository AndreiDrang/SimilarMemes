import os
import logging
from logging.config import fileConfig


os.makedirs("logs", exist_ok=True)

MEGABYTE = 1024 * 1024

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {
        "stdout": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "standard"},
        "main": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/main.log",
            "maxBytes": 50 * MEGABYTE,  # 50mb
            "backupCount": 10,
        },
        "celery": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/celery.log",
            "maxBytes": 50 * MEGABYTE,  # 50mb
            "backupCount": 10,
        },
    },
    "loggers": {
        "webmtube": {"handlers": ["stdout", "main"], "level": "DEBUG", "propagate": True},
        "webmtube.tasks": {"handlers": ["stdout", "celery"], "level": "DEBUG", "propagate": True},
        "gunicorn": {"handlers": ["stdout"], "level": "INFO", "propagate": True},
    },
}
