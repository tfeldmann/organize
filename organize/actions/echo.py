from typing_extensions import Literal

from ..utils import Template


class Echo:
    """Prints the given message.

    This can be useful to test your rules, especially in combination with placeholder
    variables.

    Args:
        msg (str): The message to print. Accepts placeholder variables.
    """

    msg: str = ""

    def __post_init__(self):
        self._msg_templ = Template.from_string(self.msg)

    def pipeline(self, res: dict) -> None:
        full_msg = self._msg_templ.render(**res)
        self.print("%s" % full_msg)
