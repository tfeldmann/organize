from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm as RichConfirm
from rich.status import Status
from rich.text import Text
from rich.theme import Theme

from organize.__version__ import __version__
from organize.utils import ChangeDetector

if TYPE_CHECKING:
    from organize.action import Action
    from organize.filter import Filter
    from organize.resource import Resource


def _highlight_path(path: Path, base_style: str, main_style: str):
    base = str(f"{path.parent}/")
    main = str(path.name)

    return Text.assemble(
        (base, base_style),
        (main, main_style),
    )


def _pipeline_source(source: Union[Filter, Action, str]):
    if hasattr(source, "filter_config"):
        src = source.filter_config.name
    elif hasattr(source, "action_config"):
        src = source.action_config.name
    else:
        src = str(source)
    return Text(f"    - ({src}) ", style="pipeline.source")


def pipeline_message(source: str, msg: str) -> None:
    return Text.assemble(
        _pipeline_source(source),
        (msg, "pipeline.msg"),
    )


def pipeline_error(source: str, msg: str):
    return Text.assemble(
        _pipeline_source(source),
        (f"ERROR! {msg}", "pipeline.error"),
    )


class Confirm(RichConfirm):
    @classmethod
    def set_source(cls, source):
        cls.validate_error_message = Text.assemble(
            _pipeline_source(source),
            ("Please enter Y or N", "prompt.invalid"),
        )


class Default:
    def __init__(self, theme: Optional[Theme] = None):
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
                    "pipeline.error": "bold red",
                    "pipeline.prompt": "bold yellow",
                    "summary.done": "bold green",
                    "summary.fail": "red",
                }
            )
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
            self.console.rule(f"[rule]:gear: {rule_name}", align="left", style="rule")

        # location changed
        if self.det_location.changed(res.basedir):
            self.det_path.reset()
            path_str = _highlight_path(
                Path(res.basedir),
                "location.base",
                "location.main",
            )
            self.console.print(path_str)

        # path changed
        if self.det_path.changed(res.path):
            path_str = _highlight_path(
                Path(res.relative_path()),
                "path.base",
                "path.main",
            )
            self.console.print(Text.assemble("  ", path_str))

    def start(self, simulate: bool, config_path: Optional[str] = None):
        self.det_rule.reset()
        self.det_location.reset()
        self.det_path.reset()

        self.simulate = simulate
        if self.simulate:
            self.console.print(Panel("SIMULATION", style="simulation"))

        self.console.print(f"organize v{__version__}")
        if config_path:
            self.console.print(f'Config: "{config_path}"')

        # if working_dir != Path("."):
        #     console.print('Working dir: "{}"'.format(working_dir))

        status_verb = "simulating" if simulate else "organizing"
        self.status.update(Text(status_verb, "status"))
        self.status.start()

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: Union[Filter, Action, str] = "",
    ):
        self.show_resource(res)
        self.console.print(pipeline_message(source=sender, msg=msg))

    def confirm(
        self,
        res: Resource,
        msg: str,
        default: str,
        sender: Union[Filter, Action, str] = "",
    ) -> bool:
        self.status.stop()
        self.show_resource(res)
        line = _pipeline_source(sender)
        line.append(msg, "pipeline.prompt")
        Confirm.set_source(sender)
        result = Confirm.ask(
            line,
            console=self.console,
            default=default,
        )
        self.status.start()
        return result

    def end(self, success_count: int, error_count: int):
        self.status.stop()
        if self.simulate:
            self.console.print(Panel("SIMULATION", style="simulation"))
