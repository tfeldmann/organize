import os
import logging
import logging.config

import appdirs
import yaml
import colorama

from .__version__ import __version__
from .utils import Path

colorama.init(autoreset=True)

# prepare config and log folders
APP_DIRS = appdirs.AppDirs("organize")

# setting the $ORGANIZE_CONFIG env variable overrides the default config path
if os.getenv("ORGANIZE_CONFIG"):
    CONFIG_PATH = Path(os.getenv("ORGANIZE_CONFIG")).resolve()
    CONFIG_DIR = CONFIG_PATH.parent
else:
    CONFIG_DIR = Path(APP_DIRS.user_config_dir)
    CONFIG_PATH = CONFIG_DIR / "config.yaml"

LOG_DIR = Path(APP_DIRS.user_log_dir)
LOG_PATH = LOG_DIR / "organize.log"

for folder in (CONFIG_DIR, LOG_DIR):
    folder.mkdir(parents=True, exist_ok=True)
if not CONFIG_PATH.exists():
    CONFIG_PATH.touch()

# configure logging
LOGGING_CONFIG = """
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
        filename: {filename}
        formatter: simple
        when: midnight
        backupCount: 30
root:
    level: DEBUG
    handlers: [file]
""".format(
    filename=str(LOG_PATH)
)
logging.config.dictConfig(yaml.load(LOGGING_CONFIG, Loader=yaml.SafeLoader))
