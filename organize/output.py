import logging
from textwrap import indent
from fs.osfs import OSFS
from rich.rule import Rule
from rich.console import Console
from rich.panel import Panel
from organize.__version__ import __version__

logger = logging.getLogger(__name__)
console = Console()


def warn(msg):
    console.print("Warning: %s" % msg, style="yellow")


class Output:
    """
    class to track the current folder / file and print only changes.
    This is needed because we only want to output the current folder and file if the
    filter or action prints something.
    """

    def __init__(self) -> None:
        self.not_found = set()
        self.curr_folder = None
        self.curr_path = None
        self.prev_folder = None
        self.prev_path = None
        self._location_target = ""

    def set_location(self, folder, path, targets="files") -> None:
        self.curr_folder = folder
        self.curr_path = path
        if targets == "dirs":
            self._location_target = "🗀"  # ":file_folder:"
        else:
            self._location_target = "🗅"  # ":page_facing_up:"

    def print_location_update(self):
        if self.curr_folder != self.prev_folder:
            if self.prev_folder is not None:
                self.print_location_spacer()
            self.print_location(self.curr_folder)
            self.prev_folder = self.curr_folder

        if self.curr_path != self.prev_path:
            self.print_path(self.curr_path)
            self.prev_path = self.curr_path

    def pipeline_message(self, name, msg, *args, **kwargs) -> None:
        """
        pre-print hook that is called everytime the moment before a filter or action is
        about to print something to the cli
        """
        self.print_location_update()
        self.print_pipeline_message(name, msg, *args, **kwargs)

    def pipeline_error(self, name, msg):
        self.print_location_update()
        self.print_pipeline_error(name, msg)

    def path_not_found(self, folderstr: str) -> None:
        if folderstr not in self.not_found:
            self.not_found.add(folderstr)
            self.print_not_found(folderstr)
            logger.warning("Path not found: %s", folderstr)

    def print_location_spacer(self):
        raise NotImplementedError

    def print_location(self, folder):
        raise NotImplementedError

    def print_path(self, path):
        raise NotImplementedError

    def print_not_found(self, path):
        raise NotImplementedError

    def print_pipeline_message(self, name, msg):
        raise NotImplementedError

    def print_pipeline_error(self, name, msg):
        raise NotImplementedError

    def print_info(self):
        raise NotImplementedError

    def print_warning(self):
        raise NotImplementedError


class ColoredOutput(Output):
    def print_info(self, rule_file, working_dir, simulate):
        console.print("organize {}".format(__version__))
        console.print('Rule file: "{}"'.format(rule_file))
        if working_dir != ".":
            console.print("Working dir: {}".format(working_dir))

    def print_warning(self, msg):
        console.print("[yellow][bold]Warning:[/bold] {}[/yellow]".format(msg))

    def print_simulation_banner(self):
        console.print(Panel("[bold green]SIMULATION", style="green"))

    def print_rule(self, rule):
        console.print(
            Rule(
                "[bold yellow]:gear: %s[/bold yellow]" % rule,
                align="left",
                style="yellow",
            )
        )

    def print_location(self, folder):
        if isinstance(folder, OSFS):
            console.print(folder.root_path, style="purple bold")
        else:
            console.print(str(folder), style="purple bold")

    def print_location_spacer(self):
        console.print()

    def print_path(self, path):
        console.print(
            indent("%s %s" % (self._location_target, path), " " * 2),
            style="italic purple",
        )

    def print_not_found(self, path):
        msg = "Path not found: {}".format(path)
        console.print(msg, style="bold yellow")

    def print_pipeline_message(self, name, msg, *args, **kwargs):
        console.print(indent("- (%s) %s" % (name, msg), " " * 4), style="green")

    def print_pipeline_error(self, name, msg):
        console.print(
            indent("- ([bold red]%s[/]) [bold red]ERROR! %s[/]" % (name, msg), " " * 4)
        )
