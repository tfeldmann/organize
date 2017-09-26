import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class Shell:

    """ Executes a shell command

        Options:
            cmd [str]
    """

    def __init__(self, cmd: str):
        self.cmd = cmd

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        full_cmd = self.cmd.format(path=path, **file_attributes)
        logger.info('Executing: $ %s', full_cmd)
        if not simulate:
            subprocess.run(full_cmd)

    def __str__(self):
        return 'Shell(cmd="%s")' % self.cmd

    def __repr__(self):
        return '<' + str(self) + '>'
