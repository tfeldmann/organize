import logging
from pathlib import Path
from .action import Action

logger = logging.getLogger(__name__)


class Python(Action):

    """
    Inline python code to execute
    """

    def __init__(self, code):
        self.code = code

    def run(self, path: Path, attrs: dict, simulate: bool):
        if simulate:
            self.print('Code not run in simulation')
        else:
            # local variables for inline function
            locals_ = attrs.copy()
            locals_['simulate'] = simulate
            locals_['path'] = path
            # replace default print function
            globals_ = globals().copy()
            globals_['print'] = self.print
            exec(self.code, globals_, locals_)
