import logging
import sys

from src.config import settings


def setup_logging():
    logger = logging.getLogger()
    if logging.getLogger().hasHandlers():
        logger.handlers.clear()

    logger.setLevel(settings.log.LOGGING_NAME)

    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[94m',
            'INFO': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'CRITICAL': '\033[95m',
        }
        RESET = '\033[0m'

        def format(self, record):
            color = self.COLORS.get(record.levelname, self.RESET)
            message = super().format(record)
            return f'{color}{message}{self.RESET}'

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
