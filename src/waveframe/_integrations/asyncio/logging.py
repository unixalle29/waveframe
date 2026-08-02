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
        level_name = f"{record.levelname}:"
        if self._use_colors:
            color = self._LEVEL_COLORS.get(record.levelno, "")
            level_name = f"{color}{level_name}{self._RESET}"
        record.levelprefix = f"{level_name:<14}"
        return super().format(record)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(DefaultFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
