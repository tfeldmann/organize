import logging
import logging.config
from functools import partial
from typing import Optional, Tuple, Union

import yaml
from fs import appfs
from fs.base import FS

from .config import Config, load_from_string


def execute(
    config: Union[Config, dict, str, None],
    simulate: bool,
    working_dir: Union[FS, str],
    tags: Optional[Tuple[str]] = None,
    skip_tags: Optional[Tuple[str]] = None,
):
    if isinstance(config, str):
        config = load_from_string(str)
    config = Config.parse_obj(config)
    config.execute(
        working_dir=working_dir,
        simulate=simulate,
        tags=tags,
        skip_tags=skip_tags,
    )


run = partial(execute, simulate=False)
sim = partial(execute, simulate=True)

with appfs.UserLogFS("organize") as log_fs:
    LOG_PATH = log_fs.getsyspath("organize.log")


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
exifread:
    level: INFO
""".format(
    filename=str(LOG_PATH)
)
logging.config.dictConfig(yaml.safe_load(LOGGING_CONFIG))
