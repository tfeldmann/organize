import textwrap
from typing import ClassVar, Dict, Optional

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Python:

    """Execute python code.

    Args:
        code (str): The python code to execute.
        run_in_simulation (bool):
            Whether to execute this code in simulation mode (Default false).
    """

    code: str
    run_in_simulation: bool = False

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="python",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self.code = textwrap.dedent(self.code)

    def __usercode__(self, print, **kwargs) -> Optional[Dict]:
        raise NotImplementedError()

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        if simulate and not self.run_in_simulation:
            output.msg(
                res=res,
                msg="** Code not run in simulation. **",
                level="warn",
                sender=self,
            )
            return

        def _output_msg(*values, sep: str = " ", end: str = ""):
            """
            the print function for the use code needs to print via the current output
            """
            msg = f"{sep.join(str(x) for x in values)}{end}"
            output.msg(res=res, msg=msg, sender=self)

        # codegen the user function with arguments as available in the resource
        kwargs = ", ".join(res.dict().keys())
        func = f"def __userfunc(print, {kwargs}):\n"
        func += textwrap.indent(self.code, "    ")
        func += "\n\nself.__usercode__ = __userfunc"
        exec(func, globals().copy(), locals().copy())
        result = self.__usercode__(print=_output_msg, **res.dict())

        # deep merge the resulting dict
        if not (result is None or isinstance(result, dict)):
            raise ValueError("The python code must return None or a dict")

        if isinstance(result, dict):
            res.deep_merge(key=self.action_config.name, data=result)
