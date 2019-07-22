import logging
from collections import defaultdict, namedtuple

from clint.textui import colored, indent, puts

from .utils import fullpath, bold, splitglob

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
        exclude_flag = folderstr.startswith("!")
        basedir, globstr = splitglob(folderstr.lstrip("!"))
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


def find_jobs(rules):
    for rule in rules:
        for folderstr, basedir, path in all_files_for_rule(rule):
            if all(f.matches(path) for f in rule.filters):
                yield Job(
                    folderstr=folderstr,
                    basedir=basedir,
                    path=path,
                    filters=rule.filters,
                    actions=rule.actions,
                )


def group_by_folder(jobs):
    result = defaultdict(list)
    for job in jobs:
        result[job.folderstr].append(job)
    return result


def filter_pipeline(job):
    result = {}
    for filter_ in job.filters:
        result.update(filter_.parse(job.path))
    return result


def action_pipeline(job: Job, attrs: dict, simulate: bool):
    try:
        current_path = None
        for action in job.actions:
            if current_path is not None:
                attrs["path"] = current_path
            new_path = action.run(attrs=attrs, simulate=simulate)
            if new_path is not None:
                current_path = new_path
    except Exception as e:
        logger.exception(e)
        action.print("%s %s" % (colored.red("ERROR!", bold=True), e))


def execute_rules(rules, simulate):
    jobs = list(find_jobs(rules))
    if not jobs:
        msg = "Nothing to do."
        logger.info(msg)
        puts(msg)
        return

    jobs_by_folder = group_by_folder(jobs)
    first = True
    if simulate:
        puts(colored.green("SIMULATION ~~~", bold=True))
    for folder, jobs in sorted(jobs_by_folder.items()):
        # newline between folders
        if not first:
            puts()
        first = False

        puts("Folder %s:" % bold(folder))
        with indent(2):
            for job in jobs:
                path = job.path
                basedir = job.basedir
                relative_path = path.relative_to(basedir)
                puts("File %s:" % bold(relative_path))
                with indent(2):
                    attrs = filter_pipeline(job)
                    attrs["path"] = path
                    attrs["basedir"] = basedir
                    attrs["relative_path"] = relative_path
                    action_pipeline(job=job, attrs=attrs, simulate=simulate)
    if simulate:
        puts(colored.green("~~~ SIMULATION", bold=True))
