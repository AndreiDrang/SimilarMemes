import os
from logging.config import dictConfig


def prepare_logging():
    # setup logs
    os.makedirs("logs", exist_ok=True)
    dictConfig(LOGGING)


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
        "database": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/database.log",
            "maxBytes": 50 * MEGABYTE,  # 50mb
            "backupCount": 10,
        },
        "gui": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/gui.log",
            "maxBytes": 50 * MEGABYTE,  # 50mb
            "backupCount": 10,
        },
        "image_processing": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/image_processing.log",
            "maxBytes": 50 * MEGABYTE,  # 50mb
            "backupCount": 10,
        },
        "indexing": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/indexing.log",
            "maxBytes": 50 * MEGABYTE,  # 50mb
            "backupCount": 10,
        },
    },
    "loggers": {
        "database": {
            "handlers": ["stdout", "database", "main"],
            "level": "DEBUG",
            "propagate": True,
        },
        "gui": {"handlers": ["stdout", "gui", "main"], "level": "DEBUG", "propagate": True},
        "image_processing": {
            "handlers": ["stdout", "image_processing", "main"],
            "level": "DEBUG",
            "propagate": True,
        },
        "indexing": {
            "handlers": ["stdout", "indexing", "main"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
