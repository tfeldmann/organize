import logging
from collections import namedtuple

from clint.textui import colored, indent, puts

from .utils import bold, dict_merge, splitglob

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


def filter_pipeline(job):
    args = dict()
    for filter_ in job.filters:
        result = filter_.run(job.path)
        if isinstance(result, dict):
            args = dict_merge(args, result)
        elif not result:
            return
    return args


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


def run_jobs(jobs, simulate):
    for job in sorted(jobs, key=lambda x: (x.folderstr, x.basedir, x.path)):
        attrs = filter_pipeline(job)
        if attrs is not None:
            path = job.path
            basedir = job.basedir
            relative_path = path.relative_to(basedir)
            yield (job.folderstr, str(relative_path))
            attrs["path"] = path
            attrs["basedir"] = basedir
            attrs["relative_path"] = relative_path
            with indent(2):
                action_pipeline(job=job, attrs=attrs, simulate=simulate)


def execute_rules(rules, simulate):
    jobs = create_jobs(rules=rules)

    if simulate:
        puts(colored.green("SIMULATION ~~~", bold=True))

    prev_folderstr = None
    for folderstr, relative_path in run_jobs(jobs=jobs, simulate=simulate):
        if folderstr != prev_folderstr:
            if prev_folderstr is not None:
                puts()
            puts("Folder %s:" % bold(folderstr))
            prev_folderstr = folderstr
        with indent(2):
            puts("File %s:" % bold(relative_path))

    if prev_folderstr is None:
        msg = "Nothing to do."
        logger.info(msg)
        puts(msg)

    if simulate:
        puts(colored.green("~~~ SIMULATION", bold=True))
