"""
logger.py
---------
Application-wide logging configuration. Logs to both console and a rotating
file at backend/logs/app.log, plus a helper to persist log entries to the
database `logs` table for the admin dashboard.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(LOG_DIR / "app.log", maxBytes=2_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def log_to_db(db, level: str, source: str, message: str) -> None:
    """Persist a log entry to the database. Best-effort; never raises."""
    try:
        from app.models import Log, LogLevel

        entry = Log(level=LogLevel(level), source=source, message=message)
        db.add(entry)
        db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Failed to write log to DB: {exc}")
