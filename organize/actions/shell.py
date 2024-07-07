import subprocess
from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render

# TODO: Terminal waterfall: https://github.com/Textualize/rich/discussions/2985


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Shell:
    """
    Executes a shell command

    Attributes:
        cmd (str): The command to execute.
        run_in_simulation (bool):
            Whether to execute in simulation mode (default = false)
        ignore_errors (bool):
            Whether to continue on returncodes != 0.
        simulation_output (str):
            The value of `{shell.output}` if run in simulation
        simulation_returncode (int):
            The value of `{shell.returncode}` if run in simulation

    Returns

    - `{shell.output}` (`str`): The stdout of the executed process.
    - `{shell.returncode}` (`int`): The returncode of the executed process.
    """

    cmd: str
    run_in_simulation: bool = False
    ignore_errors: bool = False
    simulation_output: str = "** simulation **"
    simulation_returncode: int = 0

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="shell",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._cmd = Template.from_string(self.cmd)
        self._simulation_output = Template.from_string(self.simulation_output)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        full_cmd = render(self._cmd, res.dict())

        if not simulate or self.run_in_simulation:
            output.msg(res=res, msg=f"$ {full_cmd}", sender=self)
            try:
                call = subprocess.run(
                    full_cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
                res.vars[self.action_config.name] = {
                    "output": call.stdout.decode("utf-8"),
                    "returncode": call.returncode,
                }
            except subprocess.CalledProcessError as e:
                if not self.ignore_errors:
                    raise e
                output.msg(
                    res=res,
                    msg=f"Ignoring error: {e}",
                    sender=self,
                    level="warn",
                )
                res.vars[self.action_config.name] = {
                    "output": e.output.decode("utf-8"),
                    "returncode": e.returncode,
                }

        else:
            output.msg(
                res=res,
                msg=f"** not run in simulation ** $ {full_cmd}",
                sender=self,
            )
            res.vars[self.action_config.name] = {
                "output": render(self._simulation_output, res.dict()),
                "returncode": self.simulation_returncode,
            }
