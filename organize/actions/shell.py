import logging
import subprocess

from pydantic import Field
from typing_extensions import Literal

from ..utils import Template
from .action import Action

logger = logging.getLogger(__name__)


# TODO: Terminal waterfall: https://github.com/Textualize/rich/discussions/2985
class Shell(Action):
    """
    Executes a shell command

    Args:
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

    name: Literal["shell"] = Field("shell", repr=False)

    cmd: str
    run_in_simulation: bool = False
    ignore_errors: bool = False
    simulation_output: str = "** simulation **"
    simulation_returncode: int = 0

    _cmd: Template
    _simulation_output: Template

    class ParseConfig:
        accepts_positional_arg = "cmd"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cmd = Template.from_string(self.cmd)
        self._simulation_output = Template.from_string(self.simulation_output)

    def pipeline(self, args: dict, simulate: bool):
        full_cmd = self._cmd.render(**args)

        if not simulate or self.run_in_simulation:
            # we use call instead of run to be compatible with python < 3.5
            self.print("$ %s" % full_cmd)
            logger.info('Executing command "%s" in shell.', full_cmd)
            try:
                call = subprocess.run(
                    full_cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
                return {
                    self.name: {
                        "output": call.stdout.decode("utf-8"),
                        "returncode": 0,
                    }
                }
            except subprocess.CalledProcessError as e:
                if not self.ignore_errors:
                    raise e
                return {
                    self.name: {
                        "output": e.stdout.decode("utf-8"),
                        "returncode": e.returncode,
                    }
                }
        else:
            self.print("** not run in simulation ** $ %s" % full_cmd)
            return {
                self.name: {
                    "output": self._simulation_output.render(**args),
                    "returncode": self.simulation_returncode,
                }
            }
