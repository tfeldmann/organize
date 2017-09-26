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
import shutil
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


def cli():
    # TODO: Refactor into new folder structure
    # organize
    # - commands.py:list/run
    args = docopt(__doc__, version=__version__, help=True)

    if args['config']:
        print(app_dirs.user_config_dir)
        import webbrowser
        webbrowser.open(config_dir.as_uri())

    elif args['list']:
        import inspect
        import textwrap
        from organize import filters, actions

        def heading(title, subtitle='', char='-', width=80):
            space = ' ' * (width - 2 - len(title) - len(subtitle))
            print(char * width)
            print('%s %s %s' % (title, space, subtitle))
            print()

        def content(content):
            print(textwrap.indent(content, ' ' * 4))
            print('\n')

        heading('Available filters:', char='#')
        filterclasses = inspect.getmembers(filters, inspect.isclass)
        for name, filtercls in filterclasses:
            doc = inspect.getdoc(filtercls)
            heading(name, '(filter)')
            content(doc)

        heading('Available actions:', char='#')
        actionclasses = inspect.getmembers(actions, inspect.isclass)
        for name, actioncls in actionclasses:
            doc = inspect.getdoc(actioncls)
            heading(name, '(action)')
            content(doc)

    else:
        config_path = config_dir / 'config.yaml'
        if not config_path.exists():
            shutil.copy('config.default.yaml', config_path)
        with open(config_dir / 'config.yaml') as f:
            config = Config(f.read())
        execute_rules(config.rules, simulate=args['sim'])
