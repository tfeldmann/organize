from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render


@dataclass(config=ConfigDict(extra="forbid"))
class Echo:
    """Prints the given message.

    This can be useful to test your rules, especially in combination with placeholder
    variables.

    Args:
        msg (str): The message to print. Accepts placeholder variables.
    """

    msg: str = ""

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="echo",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._msg_templ = Template.from_string(self.msg)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        full_msg = render(self._msg_templ, res.dict())
        output.msg(res, full_msg, sender=self.action_config.name)
