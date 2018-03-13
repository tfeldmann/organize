import logging
from collections import defaultdict, namedtuple

from clint.textui import colored, indent, puts

from .utils import Path, fullpath, bold

logger = logging.getLogger(__name__)


Job = namedtuple('Job', 'folder path filters actions')
Job.__doc__ = """
    :param str folder:   the folder the file was found in
    :param Path path:    the path of the file to handle
    :param list filters: the filters that apply to the path
    :param list actions: the actions which should be executed
"""


def all_files_for_rule(rule):
    for folder in rule.folders:
        globstr = '**/*.*' if rule.subfolders else '*.*'
        for path in fullpath(folder).glob(globstr):
            if path.is_file() and (
                    rule.system_files or
                    path.name not in ('thumbs.db', 'desktop.ini', '.DS_Store')):
                yield (folder, path)


def find_jobs(rules):
    for rule in rules:
        for folder, path in all_files_for_rule(rule):
            if all(f.matches(path) for f in rule.filters):
                yield Job(
                    folder=folder, path=path, filters=rule.filters,
                    actions=rule.actions)


def sort_by_folder(jobs):
    result = defaultdict(list)
    for job in jobs:
        result[job.folder].append(job)
    return result


def filter_pipeline(job):
    result = {}
    for filter_ in job.filters:
        result.update(filter_.parse(job.path))
    return result


def action_pipeline(job: Job, attrs: dict, simulate: bool):
    try:
        current_path = job.path.resolve()
        for action in job.actions:
            new_path = action.run(
                basedir=fullpath(job.folder),
                path=current_path,
                attrs=attrs,
                simulate=simulate)
            if new_path is not None:
                current_path = new_path
    except Exception as e:
        logger.exception(e)
        action.print('%s %s' % (colored.red('ERROR!', bold=True), e))


def execute_rules(rules, simulate):
    jobs = list(find_jobs(rules))
    if not jobs:
        msg = 'Nothing to do.'
        logger.info(msg)
        puts(msg)
        return

    jobs_by_folder = sort_by_folder(jobs)
    first = True
    for folder, jobs in sorted(jobs_by_folder.items()):
        # newline between folders
        if not first:
            puts()
        first = False

        puts('Folder %s:' % bold(folder))
        with indent(2):
            for job in jobs:
                puts('File %s:' % bold(job.path.name))
                with indent(2):
                    attrs = filter_pipeline(job)
                    action_pipeline(job=job, attrs=attrs, simulate=simulate)
