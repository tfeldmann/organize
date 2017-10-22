"""
The file management automation tool.

Usage:
    organize sim [-v]
    organize run [-v]
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
    -v, --verbose   Show debug information
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.
"""
import logging
from pathlib import Path

import appdirs
from docopt import docopt

from .__version__ import __version__
from .config import Config
from .core import execute_rules


app_dirs = appdirs.AppDirs('organize')
config_dir = Path(app_dirs.user_config_dir)
config_path = config_dir / 'config.yaml'
log_dir = Path(app_dirs.user_log_dir)
for p in (config_dir, log_dir):
    p.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def open_folder(path):
    import webbrowser
    webbrowser.open(path.as_uri())


def list_actions_and_filters():
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


def cli():
    args = docopt(__doc__, version=__version__, help=True)
    if args['config']:
        print(config_dir)
        open_folder(config_dir)
    elif args['list']:
        list_actions_and_filters()
    else:
        config = Config.from_file(config_path)
        execute_rules(config.rules, simulate=args['sim'])
