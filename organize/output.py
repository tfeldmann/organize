from collections import Counter
from fs.path import basename, dirname, forcedir
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from organize.__version__ import __version__

from .utils import resource_description

ICON_DIR = "🗁"
ICON_FILE = ""
INDENT = " " * 2

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
        "path.base": "dim white",
        "path.main": "white",
        "path.icon": "white",
        "pipeline.source": "cyan",
        "pipeline.msg": "white",
        "pipeline.error": "bold red",
        "summary.done": "bold green",
        "summary.fail": "red",
    }
)
console = Console(theme=theme, highlight=False)


class Prefixer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._args = None
        self._kwargs = None

    def set_prefix(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def print(self, *args, **kwargs):
        if self._args is not None:
            console.print(*self._args, **self._kwargs)
            self.reset()
        console.print(*args, **kwargs)


with_path = Prefixer()
with_newline = Prefixer()


def _highlight_path(path, base_style, main_style):
    return Text.assemble(
        (forcedir(dirname(path)), base_style),
        (basename(path), main_style),
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


def simulation_banner():
    console.print()
    console.print(Panel("SIMULATION", style="simulation"))


def spinner(simulate: bool):
    status_verb = "simulating" if simulate else "organizing"
    return console.status("[status]%s..." % status_verb)


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
        _highlight_path(path, "path.base", "path.main"),
        " ",
        (icon, "path.icon"),
    )
    with_path.set_prefix(msg)


def pipeline_message(source: str, msg: str) -> None:
    line = Text.assemble(
        INDENT * 2,
        ("- ({})".format(source), "pipeline.source"),
        (msg, "pipeline.msg"),
    )
    with_path.print(line)
    with_newline.set_prefix("")


def pipeline_error(source: str, msg: str):
    line = Text.assemble(
        INDENT * 2,
        ("- ({})".format(source), "pipeline.source"),
        ("ERROR! {}".format(msg), "pipeline.error"),
    )
    with_path.print(line)
    with_newline.set_prefix("")


def summary(count: Counter):
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
