import logging
import subprocess
from subprocess import PIPE

from schema import Optional, Or

from ..utils import Template
from .action import Action

logger = logging.getLogger(__name__)


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

    name = "shell"
    arg_schema = Or(
        str,
        {
            "cmd": str,
            Optional("run_in_simulation"): bool,
            Optional("ignore_errors"): bool,
            Optional("simulation_output"): str,
            Optional("simulation_returncode"): int,
        },
    )

    def __init__(
        self,
        cmd: str,
        run_in_simulation=False,
        ignore_errors=False,
        simulation_output="** simulation **",
        simulation_returncode=0,
    ):
        self.cmd = Template.from_string(cmd)
        self.run_in_simulation = run_in_simulation
        self.ignore_errors = ignore_errors
        self.simulation_output = Template.from_string(simulation_output)
        self.simulation_returncode = simulation_returncode

    def pipeline(self, args: dict, simulate: bool):
        full_cmd = self.cmd.render(**args)

        if not simulate or self.run_in_simulation:
            # we use call instead of run to be compatible with python < 3.5
            self.print("$ %s" % full_cmd)
            logger.info('Executing command "%s" in shell.', full_cmd)
            try:
                call = subprocess.run(
                    full_cmd,
                    check=True,
                    stdout=PIPE,
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
                    "output": self.simulation_output.render(**args),
                    "returncode": self.simulation_returncode,
                }
            }

    def __str__(self) -> str:
        return 'Shell(cmd="%s")' % self.cmd
