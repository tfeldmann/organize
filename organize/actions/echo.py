import logging

from .action import Action

logger = logging.getLogger(__name__)

from ..utils import JinjaEnv


class Echo(Action):

    """Prints the given message.

    This can be useful to test your rules, especially in combination with placeholder
    variables.

    Args:
        msg(str): The message to print. Accepts placeholder variables.
    """

    name = "echo"

    @classmethod
    def get_schema(cls):
        return {cls.name: str}

    def __init__(self, msg) -> None:
        self.msg = JinjaEnv.from_string(msg)
        self.log = logging.getLogger(__name__)

    def pipeline(self, args: dict, simulate: bool) -> None:
        full_msg = self.msg.render(**args)
        self.print("%s" % full_msg)

    def __str__(self) -> str:
        return 'Echo(msg="%s")' % self.msg
