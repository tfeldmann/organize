from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Confirm:

    """Ask for confirmation before continuing."""

    msg: str = "Continue?"
    default: bool = True

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="confirm",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._msg = Template.from_string(self.msg)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        msg = self._msg.render(**res.dict())
        result = output.confirm(
            res=res,
            msg=msg,
            sender=self,
            default="y" if self.default else "n",
        )
        if not result:
            raise StopIteration("Aborted")
