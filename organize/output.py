import logging
import shutil
from textwrap import indent
from typing import Optional, Set

from colorama import Fore, Style  # type: ignore

from .actions.action import Action
from .compat import Path
from .filters.filter import Filter

logger = logging.getLogger(__name__)


class ConsoleOutput:
    """
    class to track the current folder / file and print only changes.
    This is needed because we only want to output the current folder and file if the
    filter or action prints something.
    """

    def __init__(self) -> None:
        self.not_found = set()  # type: Set[str]
        self.curr_folder = None  # type: Optional[Path]
        self.curr_path = None  # type: Optional[Path]
        self.prev_folder = None  # type: Optional[Path]
        self.prev_path = None  # type: Optional[Path]

        Action.pre_print_hook = self.pre_print
        Filter.pre_print_hook = self.pre_print

    def set_location(self, folder: Path, path: Path) -> None:
        self.curr_folder = folder
        self.curr_path = path

    def pre_print(self) -> None:
        """
        pre-print hook that is called everytime the moment before a filter or action is
        about to print something to the cli. This is needed to NOT print a foldername
        if the filter and actions have no output.
        """
        if self.curr_folder != self.prev_folder:
            if self.prev_folder is not None:
                print()  # ensure newline between folders
            print("Folder %s%s:" % (Style.BRIGHT, self.curr_folder))
            self.prev_folder = self.curr_folder

        if self.curr_path != self.prev_path:
            print(indent("File %s%s:" % (Style.BRIGHT, self.curr_path), " " * 2))
            self.prev_path = self.curr_path

    def print_path_not_found(self, folderstr: str) -> None:
        if folderstr not in self.not_found:
            self.not_found.add(folderstr)
            msg = "Path not found: {}".format(folderstr)
            print(Fore.YELLOW + Style.BRIGHT + msg)
            logger.warning(msg)

    def simulation_banner(self):
        cols, _ = shutil.get_terminal_size(fallback=(79, 20))
        simulation_msg = " SIMULATION ".center(cols, "~")
        print(Fore.GREEN + Style.BRIGHT + simulation_msg)


console_output = ConsoleOutput()
