import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from platformdirs import user_log_dir

logger = logging.getLogger(name="organize")


def enable_logfile():
    logdir = Path(user_log_dir(appname="organize", ensure_exists=True))
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                filename=logdir / "organize-errors.log",
                backupCount=5,
                maxBytes=5_000_000,
            )
        ],
    )
