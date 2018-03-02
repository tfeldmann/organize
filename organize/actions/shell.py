import sys
import logging
import subprocess

from .action import Action
from organize.utils import Path


class Shell(Action):

    """
    Executes a shell command

    :param str cmd: The command to execute.

    Example:
      - Find all VDI Papers on your desktop, move them into documents and open the file afterwards:

        .. code-block:: yaml

          # config.yaml
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
        self.log = logging.getLogger(__name__)

    def run(self, path, attrs, simulate):  # type: (Path, dict, bool) -> None
        full_cmd = self.fill_template_tags(self.cmd, path, attrs)
        self.print('$ %s' % full_cmd)
        if not simulate:
            # we use call instead of run to be compatible with python < 3.5
            self.log.info('Executing command "%s" in shell.', full_cmd)
            subprocess.call(full_cmd, shell=True)

    def __str__(self):
        return 'Shell(cmd="%s")' % self.cmd
