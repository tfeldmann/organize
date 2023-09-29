from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, Optional, Protocol, Union

from rich import print

if TYPE_CHECKING:
    from .action import Action
    from .filter import Filter
    from .resource import Resource

# theme = Theme(
#     {
#         "info": "dim cyan",
#         "warning": "yellow",
#         "error": "bold red",
#         "simulation": "bold green",
#         "status": "bold green",
#         "rule": "bold cyan",
#         "location.fs": "yellow",
#         "location.base": "green",
#         "location.main": "bold green",
#         "path.base": "dim green",
#         "path.main": "green",
#         "path.icon": "green",
#         "pipeline.source": "cyan",
#         "pipeline.msg": "",
#         "pipeline.error": "bold red",
#         "pipeline.prompt": "bold yellow",
#         "summary.done": "bold green",
#         "summary.fail": "red",
#     }
# )
# console = Console(theme=theme, highlight=False)


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
    def start(self, simulate: bool, config_path: Optional[str] = None):
        self.prev_resource: Optional[Resource] = None

        print(f"Starte. {simulate}, {config_path}")

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
    ):
        ...

    def prompt(self, res: Resource, msg: str) -> str:
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...


class JSONL:
    def start(self, simulate: bool, config_path: Optional[str] = None):
        self._print_json(
            type="START",
            simulate=simulate,
            config_path=config_path,
        )

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: str = "",
    ):
        self._print_json(
            type="MSG",
            level=level,
            msg=msg,
            rule=res.rule.name,
            basedir=res.basedir,
            path=str(res.path),
        )

    def prompt(self, res: Resource, msg: str) -> str:
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...

    def _print_json(self, **kwargs):
        print(json.dumps(kwargs))
