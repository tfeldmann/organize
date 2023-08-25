import logging
import textwrap
from typing import Any, Dict, Iterable
from typing import Optional as tyOptional

from schema import Optional, Or

from .action import Action

logger = logging.getLogger(__name__)


class Python(Action):

    """Execute python code.

    Args:
        code (str): The python code to execute.
        run_in_simulation (bool):
            Whether to execute this code in simulation mode (Default false).
    """

    name = "python"
    arg_schema = Or(
        str,
        {
            "code": str,
            Optional("run_in_simulation"): bool,
        },
    )

    def __init__(self, code, run_in_simulation=False) -> None:
        self.code = textwrap.dedent(code)
        self.run_in_simulation = run_in_simulation

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

    def pipeline(self, args: dict, simulate: bool) -> tyOptional[Dict[str, Any]]:
        if simulate and not self.run_in_simulation:
            self.print("** Code not run in simulation. **")
            return None

        logger.info('Executing python:\n"""\n%s\n"""', self.code)
        self.create_method(name="usercode", argnames=args.keys(), code=self.code)
        self.print("Running python script.")

        result = self.usercode(**args)  # pylint: disable=assignment-from-no-return
        return result
