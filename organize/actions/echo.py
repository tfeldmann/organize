from typing_extensions import Literal

from ..utils import Template
from .action import Action


class Echo(Action):

    """Prints the given message.

    This can be useful to test your rules, especially in combination with placeholder
    variables.

    Args:
        msg (str): The message to print. Accepts placeholder variables.
    """

    name: Literal["echo"] = "echo"
    msg: str

    _msg_templ: Template

    class ParseConfig:
        accepts_positional_arg = "msg"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._msg_templ = Template.from_string(self.msg)

    def pipeline(self, args: dict, simulate: bool) -> None:
        full_msg = self._msg_templ.render(**args)
        self.print("%s" % full_msg)
