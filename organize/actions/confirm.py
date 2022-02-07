from rich.prompt import Prompt
from schema import Optional, Or

from organize import console
from organize.utils import Template

from .action import Action


class Confirm(Action):

    """Ask for confirmation before continuing."""

    name = "confirm"
    schema_support_instance_without_args = True

    arg_schema = Or(
        str,
        {
            Optional("msg"): str,
            Optional("default"): bool,
        },
    )

    def __init__(self, msg="Continue?", default=True):
        self.msg = Template.from_string(msg)
        self.default = default

    def pipeline(self, args: dict, simulate: bool):
        msg = self.msg.render(**args)
        result = console.pipeline_confirm(
            self.get_name(),
            msg,
            default=self.default,
        )
        if not result:
            raise StopIteration("Aborted")

    def __str__(self) -> str:
        return 'Confirm(msg="%s")' % self.msg
