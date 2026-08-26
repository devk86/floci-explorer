import logging
import sys

from app.core.config import get_settings

_CONFIGURED = False


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        settings = get_settings()
        message = record.getMessage()
        secret = settings.aws_secret_access_key
        if secret and secret in message:
            record.msg = message.replace(secret, "********")
            record.args = ()
        lowered = message.lower()
        if "aws_secret_access_key" in lowered and secret:
            record.msg = message.replace(secret, "********")
            record.args = ()
        return True


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RedactFilter())
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
