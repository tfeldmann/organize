import textwrap
from typing import ClassVar, Iterable

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource


@dataclass
class Python:

    """Execute python code.

    Args:
        code (str): The python code to execute.
        run_in_simulation (bool):
            Whether to execute this code in simulation mode (Default false).
    """

    code: str
    run_in_simulation: bool = False

    action_config: ClassVar = ActionConfig(
        name="python",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self.code = textwrap.dedent(self.code)

    def usercode(self, *args, **kwargs):
        pass  # will be overwritten by `create_method`

    def create_method(self, name: str, argnames: Iterable[str], code: str) -> None:
        globals_ = globals().copy()
        globals_["print"] = self.print
        locals_ = locals().copy()
        funccode = "def {fnc}__({arg}):\n{cod}\n\nself.{fnc} = {fnc}__\n".format(
            fnc=name,
            arg=", ".join(argnames),
            cod=textwrap.indent(textwrap.dedent(code), " " * 4),
        )
        exec(funccode, globals_, locals_)  # pylint: disable=exec-used

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        if simulate and not self.run_in_simulation:
            output.msg(res=res, msg="** Code not run in simulation. **", level="warn")
            return

        self.create_method(name="usercode", argnames=res.dict().keys(), code=self.code)
        res.vars.update(self.usercode(**res.dict()))
