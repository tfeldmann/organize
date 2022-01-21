from rich.console import Console
from textwrap import indent
import logging

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

    def pre_print(self) -> None:
        """
        pre-print hook that is called everytime the moment before a filter or action is
        about to print something to the cli
        """
        if self.curr_folder != self.prev_folder:
            if self.prev_folder is not None:
                self.folder_spacer()
            self.print_folder(self.curr_folder)
            self.prev_folder = self.curr_folder

        if self.curr_path != self.prev_path:
            self.print_path(self.curr_path)
            self.prev_path = self.curr_path

    def path_not_found(self, folderstr: str) -> None:
        if folderstr not in self.not_found:
            self.not_found.add(folderstr)
            self.print_not_found(folderstr)
            logger.warning("Path not found: %s", folderstr)

    def print_folder_spacer(self):
        raise NotImplementedError

    def print_folder(self, folder):
        raise NotImplementedError

    def print_path(self, path):
        raise NotImplementedError

    def print_not_found(self, path):
        raise NotImplementedError


class RichOutput(Output):
    def print_folder_spacer(self):
        console.print()

    def print_folder(self, folder):
        console.print(str(folder), style="bold")

    def print_path(self, path):
        console.print(indent(str(path), " " * 2), style="purple bold")

    def print_not_found(self, path):
        msg = "Path not found: {}".format(path)
        console.print(msg, style="bold yellow")
