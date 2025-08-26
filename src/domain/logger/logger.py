import logging
import logging.config
from pathlib import Path

from config.config import settings


def setup_logging():
    log_level_console = settings.console_log_level
    log_level_file = settings.file_log_level

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level_console,
                "formatter": "standard",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level_file,
                "formatter": "standard",
                "filename": "logs/app.log",
                "encoding": "utf8",
            },
            "file_api": {
                "class": "logging.FileHandler",
                "level": log_level_file,
                "formatter": "standard",
                "filename": "logs/api.log",
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
            },
            "src.api": {
                "handlers": ["console", "file_api"],
                "level": "INFO",
                "propagate": False,
            },
            "asyncio": {"handlers": [], "level": "WARNING", "propagate": False},
        },
    }

    Path("logs").mkdir(exist_ok=True)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Получаем логгер для каждого модуля"""
    return logging.getLogger(name)
