import logging
from collections import namedtuple
from textwrap import indent

from colorama import Fore, Style

from .utils import DotDict, splitglob

logger = logging.getLogger(__name__)


Job = namedtuple("Job", "folderstr basedir path filters actions")
Job.__doc__ = """
    :param str folderstr: the original folder definition specified in the config
    :param Path basedir:  the job's base folder
    :param Path path:     the path of the file to handle
    :param list filters:  the filters that apply to the path
    :param list actions:  the actions which should be executed
"""


def all_files_for_rule(rule):
    files = {}
    for folderstr in rule.folders:
        folderstr = folderstr.strip()
        exclude_flag = folderstr.startswith("!")
        basedir, globstr = splitglob(folderstr.lstrip("!").strip())
        if basedir.is_dir():
            if not globstr:
                globstr = "**/*" if rule.subfolders else "*"
        elif basedir.is_file():
            # this allows specifying single files
            globstr = basedir.name
            basedir = basedir.parent
        else:
            raise ValueError("Path not found: {}".format(folderstr))
        for path in basedir.glob(globstr):
            if path.is_file() and (
                rule.system_files
                or path.name not in ("thumbs.db", "desktop.ini", ".DS_Store")
            ):
                if not exclude_flag:
                    files[path] = (folderstr, basedir)
                elif path in files:
                    del files[path]
    for path, (folderstr, basedir) in files.items():
        yield (folderstr, basedir, path)


def create_jobs(rules):
    for rule in rules:
        for folderstr, basedir, path in all_files_for_rule(rule):
            yield Job(
                folderstr=folderstr,
                basedir=basedir,
                path=path,
                filters=rule.filters,
                actions=rule.actions,
            )


def filter_pipeline(filters, args):
    for filter_ in filters:
        try:
            result = filter_.pipeline(args)
            if isinstance(result, dict):
                args.update(result)
            elif not result:
                # filters might return a simple True / False.
                # Exit early if a filter does # not match.
                return False
        except Exception as e:
            logger.exception(e)
            filter_.print(Fore.RED + Style.BRIGHT + "ERROR! %s" % e)
            return False
    return True


def action_pipeline(actions, args):
    for action in actions:
        try:
            updates = action.pipeline(args)
            # jobs may return a dict with updates that should be merged into args
            if updates is not None:
                args.update(updates)
        except Exception as e:
            logger.exception(e)
            action.print(Fore.RED + Style.BRIGHT + "ERROR! %s" % e)
            return


def run_jobs(jobs, simulate):
    for job in sorted(jobs, key=lambda x: (x.folderstr, x.basedir, x.path)):
        args = DotDict(path=job.path, basedir=job.basedir, simulate=simulate)
        # the relative path should be kept even is the path changes.
        args.relative_path = args.path.relative_to(args.basedir)
        match = filter_pipeline(filters=job.filters, args=args)
        if match:
            yield (job.folderstr, args.relative_path)
            action_pipeline(actions=job.actions, args=args)


def execute_rules(rules, simulate):
    jobs = create_jobs(rules=rules)

    if simulate:
        print(Fore.GREEN + Style.BRIGHT + "SIMULATION ~~~")

    prev_folderstr = None
    for folderstr, relative_path in run_jobs(jobs=jobs, simulate=simulate):
        if folderstr != prev_folderstr:
            if prev_folderstr is not None:
                print()
            print("Folder %s:" % (Style.BRIGHT + folderstr))
            prev_folderstr = folderstr
        print(indent("File %s%s:" % (Style.BRIGHT, relative_path), " " * 2))

    if prev_folderstr is None:
        msg = "Nothing to do."
        logger.info(msg)
        print(msg)

    if simulate:
        print(Fore.GREEN + Style.BRIGHT + "~~~ SIMULATION")
