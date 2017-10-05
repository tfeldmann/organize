import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class Echo:

    """ Prints the given message to the command line

        Options:
            msg [str]: The (formatted) message string
    """

    def __init__(self, msg):
        self.msg = msg

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        full_msg = self.msg.format(path=path, **file_attributes)
        print(full_msg)

    def __str__(self):
        return 'Echo(msg="%s")' % self.msg

    def __repr__(self):
        return '<' + str(self) + '>'
