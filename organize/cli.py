"""
The file management automation tool.
Full documentation: https://organize.readthedocs.io

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

import appdirs
from clint.textui import indent, puts
from docopt import docopt

from .__version__ import __version__
from .config import Config
from .core import execute_rules
from .utils import Path, bold

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def open_folder(path):
    import webbrowser
    webbrowser.open(path.as_uri())


def list_actions_and_filters():
    import inspect
    from organize import filters, actions
    puts(bold('Available filters:'))
    with indent(2):
        for name, _ in inspect.getmembers(filters, inspect.isclass):
            puts(name)
    puts()
    puts(bold('Available actions:'))
    with indent(2):
        for name, _ in inspect.getmembers(actions, inspect.isclass):
            puts(name)


def main():
    # prepare config and log folders
    app_dirs = appdirs.AppDirs('organize')
    config_dir = Path(app_dirs.user_config_dir)
    config_path = config_dir / 'config.yaml'
    log_dir = Path(app_dirs.user_log_dir)
    for d in (config_dir, log_dir):
        d.mkdir(parents=True, exist_ok=True)

    args = docopt(__doc__, version=__version__, help=True)
    if args['config']:
        print(config_dir)
        open_folder(config_dir)
    elif args['list']:
        list_actions_and_filters()
    else:
        config = Config.from_file(config_path)
        execute_rules(config.rules, simulate=args['sim'])
