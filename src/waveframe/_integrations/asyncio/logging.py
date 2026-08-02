import logging
import sys
from typing import ClassVar


class DefaultFormatter(logging.Formatter):
    _LEVEL_COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[31;1m",
    }
    _RESET: ClassVar[str] = "\033[0m"

    def __init__(self) -> None:
        super().__init__("%(levelprefix)s %(message)s")
        self._use_colors = sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        level_name = f"{record.levelname}:".ljust(10)
        if self._use_colors:
            color = self._LEVEL_COLORS.get(record.levelno, "")
            level_name = f"{color}{level_name}{self._RESET}"
        record.levelprefix = level_name
        return super().format(record)


def configure_logging() -> None:
    logger = logging.getLogger("waveframe._integrations.asyncio")
    if logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(DefaultFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
