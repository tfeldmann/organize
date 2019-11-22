import logging
import shutil
from copy import deepcopy
from textwrap import indent
from typing import NamedTuple, Sequence, Set, Optional

from colorama import Fore, Style  # type: ignore

from .actions.action import Action
from .compat import Path
from .filters.filter import Filter
from .utils import DotDict, splitglob

logger = logging.getLogger(__name__)
SYSTEM_FILES = ("thumbs.db", "desktop.ini", ".DS_Store")

Job = NamedTuple(
    "Job",
    [
        ("folderstr", str),
        ("basedir", Path),
        ("path", Path),
        ("filters", Sequence),
        ("actions", Sequence),
    ],
)
Job.__doc__ = """
    :param str folderstr: the original folder definition specified in the config
    :param Path basedir:  the job's base folder
    :param Path path:     the path of the file to handle
    :param list filters:  the filters that apply to the path
    :param list actions:  the actions which should be executed
"""


class OutputHelper:
    """
    class to track the current folder / file and print only changes.
    This is needed because we only want to output the current folder and file if the
    filter or action prints something.
    """

    def __init__(self) -> None:
        self.not_found = set()  # type: Set[str]
        self.curr_folder = None # type: Optional[Path]
        self.curr_path = None # type: Optional[Path]
        self.prev_folder = None # type: Optional[Path]
        self.prev_path = None # type: Optional[Path]

    def set_location(self, folder: Path, path: Path) -> None:
        self.curr_folder = folder
        self.curr_path = path

    def pre_print(self) -> None:
        """
        pre-print hook that is called everytime the moment before a filter or action is
        about to print something to the cli
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


output_helper = OutputHelper()


def execute_rules(rules, simulate: bool):
    cols, _ = shutil.get_terminal_size(fallback=(79, 20))
    simulation_msg = Fore.GREEN + Style.BRIGHT + " SIMULATION ".center(cols, "~")

    jobs = create_jobs(rules=rules)

    if simulate:
        print(simulation_msg)

    failed, succeded = run_jobs(jobs=jobs, simulate=simulate)
    if succeded == failed == 0:
        msg = "Nothing to do."
        logger.info(msg)
        print(msg)

    if simulate:
        print(simulation_msg)


def create_jobs(rules):
    """ creates `Job` data structures for every path handled in each rule """
    for rule in rules:
        for folderstr, basedir, path in all_files_for_rule(rule):
            yield Job(
                folderstr=folderstr,
                basedir=basedir,
                path=path,
                filters=rule.filters,
                actions=rule.actions,
            )


def all_files_for_rule(rule):
    files = dict()
    for folderstr in rule.folders:
        folderstr = folderstr.strip()

        # check whether the file / folder is prefixed with `!` to be excluded
        exclude_flag = folderstr.startswith("!")

        # assemble glob expression
        basedir, globstr = splitglob(folderstr.lstrip("!").strip())
        if basedir.is_dir():
            if not globstr:
                globstr = "**/*" if rule.subfolders else "*"
        elif basedir.is_file():
            # this allows specifying single files
            globstr = basedir.name
            basedir = basedir.parent
        else:
            output_helper.print_path_not_found(folderstr)
            continue

        # iterate files in basedir and add to / remove from result dict
        for path in basedir.glob(globstr):
            if path.is_file() and (rule.system_files or path.name not in SYSTEM_FILES):
                if not exclude_flag:
                    files[path] = (folderstr, basedir)
                elif path in files:
                    del files[path]

    for path, (folderstr, basedir) in files.items():
        yield (folderstr, basedir, path)


def run_jobs(jobs, simulate):
    """ :returns: The number of successfully handled files """
    count = [0, 0]
    Action.pre_print_hook = output_helper.pre_print
    Filter.pre_print_hook = output_helper.pre_print

    for job in sorted(jobs, key=lambda x: (x.folderstr, x.basedir, x.path)):
        args = DotDict(path=job.path, basedir=job.basedir, simulate=simulate)
        # the relative path should be kept even if the path changes.
        args.relative_path = args.path.relative_to(args.basedir)

        output_helper.set_location(job.basedir, args.relative_path)
        match = filter_pipeline(filters=job.filters, args=args)
        if match:
            success = action_pipeline(actions=job.actions, args=args)
            count[success] += 1
    return count


def filter_pipeline(filters, args):
    """
    run the filter pipeline.
    Returns True on a match, False otherwise and updates `args` in the process.
    """
    for filter_ in filters:
        try:
            result = filter_.pipeline(deepcopy(args))
            if isinstance(result, dict):
                args.update(result)
            elif not result:
                # filters might return a simple True / False.
                # Exit early if a filter does not match.
                return False
        except Exception as e:
            logger.exception(e)
            filter_.print(Fore.RED + Style.BRIGHT + "ERROR! %s" % e)
            return False
    return True


def action_pipeline(actions, args):
    for action in actions:
        try:
            updates = action.pipeline(deepcopy(args))
            # jobs may return a dict with updates that should be merged into args
            if updates is not None:
                args.update(updates)
        except Exception as e:
            logger.exception(e)
            action.print(Fore.RED + Style.BRIGHT + "ERROR! %s" % e)
            return False
    return True
