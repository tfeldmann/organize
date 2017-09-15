import logging
from pathlib import Path
logger = logging.getLogger(__name__)


class Move:

    def __init__(self, dst):
        self.dst = dst

    def run(self, path, file_attributes, simulate):
        new_path = Path(self.dst.format(path=path, **file_attributes)).expanduser()
        if simulate:
            logger.info('Moving %s to %s', path, new_path)
        else:
            import shutil
            shutil.move(src=path, dst=new_path)
