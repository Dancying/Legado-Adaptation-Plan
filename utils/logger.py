import logging.handlers
import os
import time

import config

formatter = logging.Formatter(config.LOGS_FORMAT)
formatter.converter = time.localtime

project_logger = logging.getLogger("novelservice_logger")
project_logger.setLevel(config.LOGS_LEVEL)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
project_logger.addHandler(console_handler)

if config.LOGS_DIR:
    log_file_path = os.path.join(config.LOGS_DIR, "novelservice.log")
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when="midnight",
        interval=1,
        backupCount=15,
        encoding="UTF-8"
    )
    file_handler.setFormatter(formatter)
    project_logger.addHandler(file_handler)


def get_logger() -> logging.Logger:
    return project_logger
