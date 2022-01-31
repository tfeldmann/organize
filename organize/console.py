from fs.path import basename, dirname, forcedir, relpath
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.status import Status
from rich.prompt import Confirm as RichConfirm, Prompt as RichPrompt

from organize.__version__ import __version__

ICON_DIR = "🗁"
ICON_FILE = ""
INDENT = " " * 2

theme = Theme(
    {
        "info": "dim cyan",
        "warning": "yellow",
        "error": "red",
        "simulation": "bold green",
        "status": "bold green",
        "rule": "bold cyan",
        "location.fs": "yellow",
        "location.base": "green",
        "location.main": "bold green",
        "path.base": "dim green",
        "path.main": "green",
        "path.icon": "white",
        "pipeline.source": "cyan",
        "pipeline.msg": "white",
        "pipeline.error": "bold red",
        "pipeline.prompt": "bold yellow",
        "summary.done": "bold green",
        "summary.fail": "red",
    }
)
console = Console(theme=theme, highlight=False)
status = Status("", console=console)


class Prefixer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._args = None
        self._kwargs = None

    def set_prefix(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def ensure_prefix(self):
        if self._args is not None:
            console.print(*self._args, **self._kwargs)
            self.reset()

    def print(self, *args, **kwargs):
        self.ensure_prefix()
        console.print(*args, **kwargs)


with_path = Prefixer()
with_newline = Prefixer()


class PipelineMixin:
    @classmethod
    def set_source(cls, source):
        cls.validate_error_message = Text.assemble(
            _pipeline_base(source),
            ("Please enter Y or N", "prompt.invalid"),
        )

    def pre_prompt(self):
        with_path.ensure_prefix()


class Confirm(PipelineMixin, RichConfirm):
    pass


class Prompt(PipelineMixin, RichPrompt):
    pass


def _highlight_path(path, base_style, main_style, relative=False):
    dir_ = forcedir(dirname(path))
    if relative:
        dir_ = relpath(dir_)
    name = basename(path)
    return Text.assemble(
        (dir_, base_style),
        (name, main_style),
    )


def info(rule_file, working_dir):
    console.print("organize {}".format(__version__))
    console.print('Config file: "{}"'.format(rule_file))
    if working_dir != ".":
        console.print("Working dir: {}".format(working_dir))


def warn(msg, title="Warning"):
    console.print("[warning][b]{}:[/b] {}[/warning]".format(title, msg))


def deprecated(msg):
    warn(msg, title="Deprecated")


def error(msg, title="Error"):
    console.print("[error][b]{}:[/b] {}[/error]".format(title, msg))


def simulation_banner():
    console.print()
    console.print(Panel("SIMULATION", style="simulation"))


def spinner(simulate: bool):
    status_verb = "simulating" if simulate else "organizing"
    status.update(Text(status_verb, "status"))
    status.start()


def rule(rule):
    console.print()
    console.rule("[rule]:gear: %s" % rule, align="left", style="rule")
    with_newline.reset()


def location(fs, path):
    result = Text()
    if fs.hassyspath(path):
        syspath = fs.getsyspath(path)
        result = _highlight_path(syspath.rstrip("/"), "location.base", "location.main")
    else:
        result = Text.assemble(
            (str(fs), "location.fs"),
            " ",
            _highlight_path(path.rstrip("/"), "location.base", "location.main"),
        )
    with_newline.print(result)


def path(fs, path):
    icon = ICON_DIR if fs.isdir(path) else ICON_FILE
    msg = Text.assemble(
        INDENT,
        _highlight_path(path, "path.base", "path.main", relative=True),
        " ",
        (icon, "path.icon"),
    )
    with_path.set_prefix(msg)


def _pipeline_base(source: str):
    return Text.assemble(
        INDENT * 2,
        ("- ({}) ".format(source), "pipeline.source"),
    )


def pipeline_message(source: str, msg: str) -> None:
    line = Text.assemble(
        _pipeline_base(source),
        (msg, "pipeline.msg"),
    )
    with_path.print(line)
    with_newline.set_prefix("")


def pipeline_error(source: str, msg: str):
    line = _pipeline_base(source)
    line.append("ERROR! {}".format(msg), "pipeline.error")
    with_path.print(line)
    with_newline.set_prefix("")


def pipeline_confirm(source: str, msg: str, default: bool):
    status.stop()
    line = _pipeline_base(source)
    line.append(msg, "pipeline.prompt")
    Confirm.set_source(source)
    result = Confirm.ask(
        line,
        console=console,
        default=default,
    )
    with_newline.set_prefix("")
    status.start()
    return result


def summary(count: dict):
    status.stop()
    console.print()
    if not sum(count.values()):
        console.print("Nothing to do.")
    else:
        result = Text.assemble(
            ("success {done}".format(**count), "summary.done"),
            " / ",
            ("fail {fail}".format(**count), "summary.fail"),
        )
        console.print(result)
