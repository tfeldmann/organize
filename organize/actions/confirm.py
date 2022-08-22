from typing_extensions import Literal

from organize import console
from organize.utils import Template

from .action import Action


class Confirm(Action):

    """Ask for confirmation before continuing."""

    name: Literal["confirm"] = "confirm"
    msg: str = "Continue?"
    default: bool = True

    _msg: Template

    class Config:
        accepts_positional_arg = "msg"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._msg = Template.from_string(self.msg)

    def pipeline(self, args: dict, simulate: bool):
        msg = self._msg.render(**args)
        result = console.pipeline_confirm(self.name, msg, default=self.default)
        if not result:
            raise StopIteration("Aborted")
