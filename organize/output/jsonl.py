from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

from pydantic import BaseModel

from ._sender import sender_name

if TYPE_CHECKING:
    from organize.resource import Resource

    from ._sender import SenderType


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


class Report(BaseModel):
    type: Literal["REPORT"] = "REPORT"
    success_count: int
    error_count: int


EventType = Union[Start, Msg, Report]


def ask_confirm(text):
    while True:
        answer = input(f"{text} [y/n]: ").lower()
        if answer in ("j", "y", "ja", "yes"):
            return True
        if answer in ("n", "no", "nein"):
            return False


class JSONL:
    def __init__(self, auto_confirm: bool = False) -> None:
        self.auto_confirm = auto_confirm

    def start(self, simulate: bool, config_path: Optional[Path] = None) -> None:
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
        sender: SenderType = "",
    ) -> None:
        rule = res.rule.name if res.rule and res.rule.name else ""
        basedir = res.basedir or ""
        self.emit_event(
            Msg(
                type="MSG",
                level=level,
                msg=msg,
                rule=rule,
                basedir=str(basedir),
                path=str(res.path),
                sender=sender_name(sender),
            )
        )

    def prompt(self, res: Resource, msg: str) -> str:
        raise ValueError("prompting not supported in JSONL output")

    def confirm(self, res: Resource, msg: str) -> bool:
        if self.auto_confirm:
            return True
        return ask_confirm(msg)

    def end(self, success_count: int, error_count: int) -> None:
        report = Report(
            success_count=success_count,
            error_count=error_count,
        )
        self.emit_event(report)

    def emit_event(self, event: EventType) -> None:
        print(event.model_dump_json())
