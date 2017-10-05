import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Trash:

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        from send2trash import send2trash
        logger.info('Trashing "%s"', path)
        if not simulate:
            send2trash(path)
