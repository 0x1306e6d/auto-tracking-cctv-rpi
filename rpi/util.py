import logging
import logging.config

from rpi.config import (
    LOGGING_FILE_NAME
)


def setup_logging_by_file(file_name=LOGGING_FILE_NAME):
    """Setup logging configuration by file."""

    if file_name is None:
        file_name = LOGGING_FILE_NAME

    logging.config.fileConfig(file_name)
