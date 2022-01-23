import logging

from rich.prompt import Prompt
from ..output import console
from .action import Action

logger = logging.getLogger(__name__)

# TODO not working right now


class Confirm(Action):
    def __init__(self, msg, default):
        self.msg = msg
        self.default = default
        self.prompt = Prompt(console=console)

    def pipeline(self, args: dict, simulate: bool):
        chosen = self.prompt.ask("", default=self.default)
        self.print(chosen)

    def __str__(self) -> str:
        return 'Echo(msg="%s")' % self.msg

    name = "confirm"
