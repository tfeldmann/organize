from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

from pydantic import BaseModel

from ._sender import sender_name
from .output import Level

if TYPE_CHECKING:
    from organize.resource import Resource

    from ._sender import SenderType


class Start(BaseModel):
    type: Literal["START"] = "START"
    simulate: bool
    config_path: Optional[Path]
    working_dir: Path


class Msg(BaseModel):
    type: Literal["MSG"] = "MSG"
    level: Level = "info"
    path: Optional[Path]
    basedir: Optional[Path]
    sender: str
    msg: str
    rule_nr: int
    rule_name: str


class Confirm(BaseModel):
    type: Literal["CONFIRM"] = "CONFIRM"
    path: Optional[Path]
    basedir: Optional[Path]
    sender: str
    msg: str
    default: bool
    rule_nr: int
    rule_name: str


class Report(BaseModel):
    type: Literal["REPORT"] = "REPORT"
    success_count: int
    error_count: int


EventType = Union[Start, Msg, Confirm, Report]


class JSONL:
    def __init__(self, auto_confirm: bool = False) -> None:
        self.auto_confirm = auto_confirm

    def start(
        self,
        simulate: bool,
        config_path: Optional[Path],
        working_dir: Path,
    ) -> None:
        self.emit_event(
            Start(
                simulate=simulate,
                config_path=config_path.resolve() if config_path else None,
                working_dir=working_dir.resolve(),
            )
        )

    def msg(
        self,
        res: Resource,
        msg: str,
        sender: SenderType,
        level: Level = "info",
    ) -> None:
        self.emit_event(
            Msg(
                level=level,
                path=res.path,
                basedir=res.basedir,
                sender=sender_name(sender),
                msg=msg,
                rule_nr=res.rule_nr,
                rule_name=res.rule.name if res.rule and res.rule.name else "",
            )
        )

    def confirm(
        self,
        res: Resource,
        msg: str,
        default: bool,
        sender: SenderType,
    ) -> bool:
        if self.auto_confirm:
            return True
        self.emit_event(
            Confirm(
                path=res.path,
                basedir=res.basedir,
                sender=sender_name(sender),
                msg=msg,
                default=default,
                rule_nr=res.rule_nr,
                rule_name=res.rule.name if res.rule and res.rule.name else "",
            )
        )
        answer = input().lower()
        if answer == "":
            return default
        elif answer in ("j", "y", "ja", "yes", "1"):
            return True
        return False

    def end(self, success_count: int, error_count: int) -> None:
        report = Report(
            success_count=success_count,
            error_count=error_count,
        )
        self.emit_event(report)

    def emit_event(self, event: EventType) -> None:
        print(event.model_dump_json())
