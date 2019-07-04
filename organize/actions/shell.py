import logging
import subprocess

from .action import Action


class Shell(Action):

    """
    Executes a shell command

    :param str cmd: The command to execute.

    Example:
      - (macOS) Open all pdfs on your desktop:

        .. code-block:: yaml
          :caption: config.yaml

          rules:
            - folders: '~/Desktop'
              filters:
                - extension: pdf
              actions:
                - shell: 'open "{path}"'
    """

    def __init__(self, cmd: str):
        self.cmd = cmd
        self.log = logging.getLogger(__name__)

    def run(self, attrs: dict, simulate: bool):
        full_cmd = self.fill_template_tags(self.cmd, attrs)
        self.print("$ %s" % full_cmd)
        if not simulate:
            # we use call instead of run to be compatible with python < 3.5
            self.log.info('Executing command "%s" in shell.', full_cmd)
            subprocess.call(full_cmd, shell=True)

    def __str__(self):
        return 'Shell(cmd="%s")' % self.cmd
