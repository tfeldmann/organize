from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Protocol, Union

from pydantic import BaseModel
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from organize.__version__ import __version__

if TYPE_CHECKING:
    from .action import Action
    from .filter import Filter
    from .resource import Resource


class Output(Protocol):
    def start(self, simulate: bool, config_path: Optional[str] = None):
        ...

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: Union[Filter, Action, str] = "",
    ):
        ...

    def prompt(self, res: Resource, msg: str) -> str:
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...


class Rich:
    def __init__(self):
        theme = Theme(
            {
                "info": "dim cyan",
                "warning": "yellow",
                "error": "bold red",
                "simulation": "bold green",
                "status": "bold green",
                "rule": "bold cyan",
                "location.fs": "yellow",
                "location.base": "green",
                "location.main": "bold green",
                "path.base": "dim green",
                "path.main": "green",
                "path.icon": "green",
                "pipeline.source": "cyan",
                "pipeline.msg": "",
                "pipeline.error": "bold red",
                "pipeline.prompt": "bold yellow",
                "summary.done": "bold green",
                "summary.fail": "red",
            }
        )
        self.console = Console(theme=theme, highlight=False)

    def start(self, simulate: bool, config_path: Optional[str] = None):
        self.prev_res: Optional[Resource] = None
        if simulate:
            self.console.print(Panel("SIMULATION", style="simulation"))

        self.console.print(f"organize {__version__}")
        self.console.print(f'Config: "{config_path}"')

        # if working_dir != Path("."):
        #     console.print('Working dir: "{}"'.format(working_dir))

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: Union[Filter, Action, str] = "",
    ):
        if not self.prev_res or self.prev_res.rule != res.rule:
            self.console.rule(f"[rule]:gear: {res.rule}", align="left", style="rule")
        if not self.prev_res or self.prev_res.basedir != res.basedir:
            self.console.print(res.basedir, style="location.base")
        if not self.prev_res or self.prev_res.path != res.path:
            self.console.print(f"  {res.path}", style="path.base")
        self.console.print(f"    - ({sender}) {level}: {msg}", style="pipeline.source")
        self.prev_res = res

    def prompt(self, res: Resource, msg: str) -> str:
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...


class Start(BaseModel):
    type: Literal["START"] = "START"
    simulate: bool
    config_path: Optional[str] = None


class Msg(BaseModel):
    type: Literal["MSG"] = "MSG"
    level: Literal["info", "warn", "error"] = "info"
    msg: str
    rule: str
    basedir: str
    path: str
    sender: str = ""


Event = Union[Start, Msg]


class RawOutput:
    def start(self, simulate: bool, config_path: Optional[str] = None):
        self._output(
            Start(
                type="START",
                simulate=simulate,
                config_path=config_path,
            )
        )

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: str = "",
    ):
        self._output(
            Msg(
                type="MSG",
                level=level,
                msg=msg,
                rule=res.rule.name or "" if res.rule else "",
                basedir=res.basedir,
                path=str(res.path),
            )
        )

    def prompt(self, res: Resource, msg: str) -> str:
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...

    def _output(self, item: Event):
        ...


class QueueOutput(RawOutput):
    def __init__(self):
        self.queue = []

    def start(self, *args, **kwargs):
        self.queue.clear()
        super().start(*args, **kwargs)

    def _output(self, item: Event):
        self.queue.append(item)

    @property
    def messages(self):
        return [x for x in self.queue if x.type == "MSG"]


class JSONL(RawOutput):
    def _output(self, item: Event):
        print(item.model_dump_json())
