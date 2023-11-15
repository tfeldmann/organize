from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from organize.action import Action
    from organize.filter import Filter
    from organize.resource import Resource


class Start(BaseModel):
    type: Literal["START"] = "START"
    simulate: bool
    config_path: Optional[Path] = None


class Msg(BaseModel):
    type: Literal["MSG"] = "MSG"
    level: Literal["info", "warn", "error"] = "info"
    msg: str
    rule: str
    basedir: str
    path: str
    sender: str = ""


EventType = Union[Start, Msg]


class JSONL:
    def start(self, simulate: bool, config_path: Optional[Path] = None):
        self.emit_event(
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
        sender: Union[Filter, Action, str] = "",
    ):
        try:
            rule = res.rule.name or ""
        except AttributeError:
            rule = ""
        basedir = res.basedir or ""
        self.emit_event(
            Msg(
                type="MSG",
                level=level,
                msg=msg,
                rule=rule,
                basedir=str(basedir),
                path=str(res.path),
            )
        )

    def prompt(self, res: Resource, msg: str) -> str:
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...

    def emit_event(self, event: EventType):
        print(event.model_dump_json())
