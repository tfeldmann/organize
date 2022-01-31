from rich.prompt import Prompt

from organize import console
from organize.utils import Template

from .action import Action


class Confirm(Action):

    name = "confirm"
    schema_support_instance_without_args = True

    def __init__(self, msg="Continue?", default=True):
        self.msg = Template.from_string(msg)
        self.default = default
        self.prompt = Prompt(console=console)

    def pipeline(self, args: dict, simulate: bool):
        msg = self.msg.render(**args)
        result = console.pipeline_confirm(
            self.get_name(),
            msg,
            default=self.default,
        )
        if not result:
            raise ValueError("Aborted")

    def __str__(self) -> str:
        return 'Confirm(msg="%s")' % self.msg
