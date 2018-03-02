"""
The file management automation tool.

Usage:
    organize sim
    organize run
    organize config [--open-folder | --path | --debug]
    organize list
    organize --help
    organize --version

Arguments:
    sim             Simulate organizing your files. This allows you to check your rules.
    run             Organizes your files according to your rules.
    config          Open the configuration file in $EDITOR.
    list            List available filters and actions.
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.

organize config options:
    -o, --open-folder  Open the folder containing the configuration files.
    -p, --path         Show the path of the configuration file.
    -d, --debug        Print the current configuration for debugging purposes.

Full documentation: https://organize.readthedocs.io
"""
import logging
import logging.config
import os
import subprocess

import appdirs
import yaml
from clint.textui import indent, puts
from docopt import docopt

from .__version__ import __version__
from .config import Config
from .core import execute_rules
from .utils import Path, bold

logger = logging.getLogger(__name__)

LOGGING = """
version: 1
formatters:
    simple:
        format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: simple
        stream: ext://sys.stdout
loggers:
    simpleExample:
        level: DEBUG
        handlers: [console]
        propagate: no
root:
    level: DEBUG
    handlers: [console]
"""
logging.config.dictConfig(yaml.load(LOGGING))


def open_in_filemanager(path):
    import webbrowser
    webbrowser.open(path.as_uri())


def list_actions_and_filters():
    import inspect
    from organize import filters, actions
    puts(bold('Filters:'))
    with indent(2):
        for name, _ in inspect.getmembers(filters, inspect.isclass):
            puts(name)
    puts()
    puts(bold('Actions:'))
    with indent(2):
        for name, _ in inspect.getmembers(actions, inspect.isclass):
            puts(name)


def config_debug(config_path):
    """ prints the config with resolved aliases and tries to parse rules """
    try:
        config = Config.from_file(config_path)
        print(config.yaml())
        _ = config.rules
    except Config.Error as exc:
        print(exc)


def open_in_editor(path):
    """ open the config file in $EDITOR or default text editor """
    # create empty config file if it does not exist
    if not path.exists():
        path.touch()
    editor = os.getenv('EDITOR')
    if editor:
        subprocess.call([editor, str(path)])
    else:
        open_in_filemanager(path)


def main():
    # prepare config and log folders
    app_dirs = appdirs.AppDirs('organize')
    config_dir = Path(app_dirs.user_config_dir)
    config_path = config_dir / 'config.yaml'
    log_dir = Path(app_dirs.user_log_dir)
    for folder in (config_dir, log_dir):
        folder.mkdir(parents=True, exist_ok=True)

    args = docopt(__doc__, version=__version__, help=True)
    if args['config']:
        if args['--open-folder']:
            open_in_filemanager(config_dir)
        elif args['--path']:
            print(str(config_path))
        elif args['--debug']:
            config_debug(config_path)
        else:
            open_in_editor(config_path)

    elif args['list']:
        list_actions_and_filters()
    else:
        try:
            config = Config.from_file(config_path)
            execute_rules(config.rules, simulate=args['sim'])
        except Config.Error as e:
            print('There is a problem in your config file:')
            print(e)
