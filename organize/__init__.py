import logging
import logging.config

import yaml
from fs import appfs

with appfs.UserLogFS("organize") as log_fs:
    LOG_PATH = log_fs.getsyspath("organize.log")

# configure logging
LOGGING_CONFIG = f"""
version: 1
disable_existing_loggers: false
formatters:
    simple:
        format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: simple
        stream: ext://sys.stdout
    file:
        class: logging.handlers.TimedRotatingFileHandler
        level: DEBUG
        filename: {str(LOG_PATH)}
        encoding: utf-8
        formatter: simple
        when: midnight
        backupCount: 30
root:
    level: DEBUG
    handlers: [file]
exifread:
    level: INFO
"""
logging.config.dictConfig(yaml.safe_load(LOGGING_CONFIG))
