"""
The personal file management tool.

Usage:
    organize sim
    organize run
    organize config
    organize list
    organize --help
    organize --version

Arguments:
    sim             Simulate organizing your files. This allows you to check your rules.
    run             Organizes your files according to your rules.
    config          Open the organize config folder
    list            List available filters and actions

Options:
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.
"""
import logging
from pathlib import Path
from collections import namedtuple

import appdirs
from docopt import docopt

from .__version__ import __version__
from .config import Config


app_dirs = appdirs.AppDirs('organize')
config_dir = Path(app_dirs.user_config_dir)
log_dir = Path(app_dirs.user_log_dir)
for p in (config_dir, log_dir):
    p.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def all_pathes(rule):
    for folder in rule.folders:
        yield from Path(folder).expanduser().glob('*.*')


def find_jobs(rules):
    Job = namedtuple('Job', 'path filters actions')
    result = []
    for rule in rules:
        for path in all_pathes(rule):
            if all(f.matches(path) for f in rule.filters):
                job = Job(
                    path=path,
                    filters=rule.filters,
                    actions=rule.actions)
                result.append(job)
    return list(sorted(result, key=lambda j: j.path))


def execute_rules(rules, simulate: bool):
    def first(x):
        return x[0]

    jobs = find_jobs(rules)
    # TODO: warning for multiple rules applying to the same path
    if not jobs:
        print('Nothing to do.')
    else:
        logger.debug(jobs)
        for job in jobs:
            logger.info('File %s', job.path)
            file_attributes = first(job.filters).parse(job.path)
            first(job.actions).run(
                path=job.path.resolve(),
                file_attributes=file_attributes,
                simulate=simulate)


def main():
    args = docopt(__doc__, version=__version__, help=True)

    if args['config']:
        print(app_dirs.user_config_dir)
        import webbrowser
        webbrowser.open(config_dir.as_uri())

    elif args['list']:
        import inspect
        import textwrap
        from organize import filters, actions
        indentation = '    '

        filterclasses = inspect.getmembers(filters, inspect.isclass)
        print('Available filters:\n')
        for name, filtercls in filterclasses:
            sig = inspect.signature(filtercls.__init__)
            doc = textwrap.indent(inspect.getdoc(filtercls), indentation)
            print('- %s%s' % (name, sig))
            print('%s\n' % doc)

        print()
        actionclasses = inspect.getmembers(actions, inspect.isclass)
        print('Available actions:\n')
        for name, actioncls in actionclasses:
            sig = inspect.signature(actioncls.__init__)
            doc = textwrap.indent(inspect.getdoc(actioncls), indentation)
            print('- %s%s' % (name, sig))
            print('%s\n' % doc)

    else:
        with open('config.yaml') as f:
            config = Config(f.read())
        execute_rules(config.rules, simulate=args['sim'])
