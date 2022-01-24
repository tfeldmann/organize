import logging
from textwrap import indent
from fs.osfs import OSFS
from rich.rule import Rule
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()


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

    def set_location(self, folder, path) -> None:
        self.curr_folder = folder
        self.curr_path = path

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


class RichOutput(Output):
    def print_simulation_banner(self):
        console.print(Panel("[bold green]SIMULATION", style="green"))

    def print_rule(self, rule):
        console.print(Rule(rule, align="left", style="gray"), style="bold")

    def print_location(self, folder):
        if isinstance(folder, OSFS):
            console.print(folder.root_path)
        else:
            console.print(str(folder), style="bold")

    def print_location_spacer(self):
        console.print()

    def print_path(self, path):
        console.print(indent(str(path), " " * 2), style="purple bold")

    def print_not_found(self, path):
        msg = "Path not found: {}".format(path)
        console.print(msg, style="bold yellow")

    def print_pipeline_message(self, name, msg, *args, **kwargs):
        console.print(indent("- (%s) %s" % (name, msg), " " * 4))

    def print_pipeline_error(self, name, msg):
        console.print(
            indent("- ([bold red]%s[/]) [bold red]ERROR! %s[/]" % (name, msg), " " * 4)
        )
