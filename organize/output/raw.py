from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from organize.resource import Resource


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
