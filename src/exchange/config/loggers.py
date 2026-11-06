import logging.config
from pathlib import Path

from exchange.config.settings import settings

LOG_FILE = settings.LOG_FILE
MAX_BYTES = settings.LOG_MAX_BYTES
BACKUP_COUNT = settings.LOG_BACKUP_COUNT

log_dir = Path(LOG_FILE).parent
if log_dir != Path("."):
    log_dir.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT,
            "filename": LOG_FILE,
            "formatter": "standard",
            "mode": "a",
            "encoding": "utf8",
        },
    },
    "loggers": {
        "exchange_service": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

api_logger = logging.getLogger("exchange_service")
