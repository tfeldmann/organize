import logging
import subprocess
from pathlib import Path
from .action import Action

logger = logging.getLogger(__name__)


class Shell(Action):

    """
    Executes a shell command

    :param str cmd: The command to execute.

    Example:

    - Find all VDI Papers on your desktop, move them into documents and open the file afterwards

      .. code-block: yaml

        rules:
          - folders: '~/Desktop'
            filters:
              - PaperVDI
            actions:
              - Move: '~/Documents/VDI Nachrichten/VDI {vdi.year}-{vdi.month:02}-{vdi.day:02}.pdf'
              - Shell: 'open "{path}"'
    """

    def __init__(self, cmd: str):
        self.cmd = cmd

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        full_cmd = self.cmd.format(path=path, **file_attributes)
        logger.info('Executing: $ %s', full_cmd)
        if not simulate:
            subprocess.run(full_cmd, shell=True)

    def __str__(self):
        return 'Shell(cmd="%s")' % self.cmd
