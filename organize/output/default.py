from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm as RichConfirm
from rich.status import Status
from rich.theme import Theme

from organize.utils import ChangeDetector

from ._sender import sender_name
from .output import Level

if TYPE_CHECKING:
    from typing import List

    from organize.resource import Resource

    from ._sender import SenderType


def format_path(path: Path, base_style: str, main_style: str) -> str:
    base = escape(str(f"{path.parent}/"))
    main = escape(str(path.name))
    return f"[{base_style}]{base}[/][{main_style}]{main}[/]"


MSG_STYLE: Dict[Level, str] = {
    "info": "[pipeline.msg]",
    "warn": "[pipeline.warn]",
    "error": "[pipeline.error]ERROR! ",
}


def format_msg(
    msg: str,
    level: Level,
    sender: SenderType,
    standalone: bool,
    escape_msg: bool = True,
) -> str:
    _msg = escape(msg) if escape_msg else msg
    indent = "    - " if not standalone else ""

    fmt_sender = f"([pipeline.source]{escape(sender_name(sender))}[/])"
    fmt_msg = f"{MSG_STYLE[level]}{_msg}[/]"
    return f"{indent}{fmt_sender} {fmt_msg}"


class Confirm(RichConfirm):
    @classmethod
    def set_error_msg(cls, msg: str) -> None:
        cls.validate_error_message = msg


class Default:
    def __init__(self, theme: Optional[Theme] = None, errors_only: bool = False):
        if theme is None:
            theme = Theme(
                {
                    "info": "dim cyan",
                    "warning": "yellow",
                    "error": "bold red",
                    "simulation": "bold green",
                    "status": "bold green",
                    "rule": "bold cyan",
                    "location.base": "green",
                    "location.main": "bold green",
                    "path.base": "dim green",
                    "path.main": "green",
                    "pipeline.source": "cyan",
                    "pipeline.msg": "",
                    "pipeline.warn": "yellow",
                    "pipeline.error": "bold red",
                    "pipeline.prompt": "bold yellow",
                    "summary.done": "bold green",
                    "summary.fail": "red",
                }
            )
        self.errors_only = errors_only
        self.msg_queue: List[str] = []
        self.det_resource = ChangeDetector()

        self.console = Console(theme=theme, highlight=False)

        self.status = Status("", console=self.console)
        self.det_rule = ChangeDetector()
        self.det_location = ChangeDetector()
        self.det_path = ChangeDetector()
        self.simulate = False

    def show_resource(self, res: Resource):
        # rule changed
        if self.det_rule.changed(res.rule):
            self.det_location.reset()
            self.det_path.reset()
            self.console.print()
            rule_name = f"Rule #{res.rule_nr}"
            if res.rule is not None and res.rule.name is not None:
                rule_name += f": {res.rule.name}"
            self.console.rule(
                f"[rule]:gear: {escape(rule_name)}",
                align="left",
                style="rule",
            )

        # location changed
        if self.det_location.changed(res.basedir):
            self.det_path.reset()
            if res.basedir:
                path_str = format_path(
                    Path(res.basedir),
                    "location.base",
                    "location.main",
                )
                self.console.print(path_str)

        # path changed
        if self.det_path.changed(res.path):
            relative_path = res.relative_path()
            if relative_path is not None:
                path_str = format_path(relative_path, "path.base", "path.main")
                self.console.print(f"  {path_str}")

    def start(
        self,
        simulate: bool,
        config_path: Optional[Path],
        working_dir: Path,
    ) -> None:
        self.det_rule.reset()
        self.det_location.reset()
        self.det_path.reset()

        self.simulate = simulate
        if self.simulate:
            self.console.print(Panel("SIMULATION", style="simulation"))

        if working_dir.resolve() != Path(".").resolve():
            self.console.print(f'Working dir: "{escape(str(working_dir))}"')
        if config_path:
            self.console.print(f'Config: "{escape(str(config_path))}"')

        status_verb = "simulating" if simulate else "organizing"
        self.status.update(f"[status]{status_verb}[/]")
        self.status.start()

    def msg(
        self,
        res: Resource,
        msg: str,
        sender: SenderType,
        level: Level = "info",
    ) -> None:
        msg = format_msg(
            msg=msg,
            level=level,
            sender=sender,
            standalone=res.path is None,
        )

        if self.errors_only:
            if self.det_resource.changed(res):
                self.msg_queue.clear()
            self.msg_queue.append(msg)
            if level == "error":
                self.show_resource(res)
                for msg in self.msg_queue:
                    self.console.print(msg)
                self.msg_queue.clear()
        else:
            self.show_resource(res)
            self.console.print(msg)

    def confirm(
        self,
        res: Resource,
        msg: str,
        default: bool,
        sender: SenderType,
    ) -> bool:
        self.status.stop()
        self.show_resource(res)
        msg_prompt = format_msg(
            msg=f"[pipeline.prompt]{escape(msg)}[/]",
            level="info",
            sender=sender,
            standalone=res.path is None,
            escape_msg=False,
        )
        msg_invalid = format_msg(
            msg="[prompt.invalid]Please enter Y or N[/]",
            level="info",
            sender=sender,
            standalone=res.path is None,
            escape_msg=False,
        )
        Confirm.set_error_msg(msg=msg_invalid)
        result = Confirm.ask(prompt=msg_prompt, console=self.console, default=default)
        self.status.start()
        return result

    def end(self, success_count: int, error_count: int):
        self.status.stop()
        self.console.print()
        if success_count == 0 and error_count == 0:
            self.console.print("[summary.done]Nothing to do[/]")
        else:
            msg = (
                f"[summary.done]success {success_count}[/] / "
                f"[summary.fail]fail {error_count}[/]"
            )
            self.console.print(msg)
        if self.simulate:
            self.console.print(Panel("SIMULATION", style="simulation"))
