from ..utils import Template
from .action import Action


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
        self.msg = Template.from_string(msg)

    def pipeline(self, args: dict, simulate: bool) -> None:
        full_msg = self.msg.render(**args)
        self.print("%s" % full_msg)

    def __str__(self) -> str:
        return 'Echo(msg="%s")' % self.msg
