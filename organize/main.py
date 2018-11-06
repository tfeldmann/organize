"""
The file management automation tool.

Usage:
    organize sim [<config_path>]
    organize run [<config_path>]
    organize config [--open-folder | --path | --debug]
    organize list
    organize --help
    organize --version

Arguments:
    sim             Simulate a run. Does not touch your files.
    run             Organizes your files according to your rules.
    config          Open the configuration file in $EDITOR.
    list            List available filters and actions.
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.

Options:
    -o, --open-folder  Open the folder containing the configuration files.
    -p, --path         Show the path to the configuration file.
    -d, --debug        Debug your configuration file.

Full documentation: https://organize.readthedocs.io
"""
import logging
import logging.config
import os
import subprocess
import sys

import appdirs
import yaml
from clint.textui import colored, indent, puts
from docopt import docopt

from .__version__ import __version__
from .config import Config
from .core import execute_rules
from .utils import Path, bold, flatten, fullpath

# prepare config and log folders
app_dirs = appdirs.AppDirs('organize')
config_dir = Path(app_dirs.user_config_dir)
config_path = config_dir / 'config.yaml'
log_dir = Path(app_dirs.user_log_dir)
log_path = log_dir / 'organize.log'

for folder in (config_dir, log_dir):
    folder.mkdir(parents=True, exist_ok=True)
if not config_path.exists():
    config_path.touch()

# configure logging
LOGGING = """
version: 1
disable_existing_loggers: false
formatters:
    simple:
        format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: simple
        stream: ext://sys.stdout
    file:
        class: logging.handlers.TimedRotatingFileHandler
        level: DEBUG
        filename: {filename}
        formatter: simple
        when: midnight
        backupCount: 35
root:
    level: DEBUG
    handlers: [file]
""".format(filename=str(log_path))
logging.config.dictConfig(yaml.load(LOGGING, Loader=yaml.SafeLoader))
logger = logging.getLogger(__name__)


def main():
    """ entry point for the command line interface """
    args = docopt(__doc__, version=__version__, help=True)
    # > organize config
    if args['config']:
        if args['--open-folder']:
            open_in_filemanager(config_dir)
        elif args['--path']:
            puts(str(config_path))
        elif args['--debug']:
            config_debug()
        else:
            config_edit()
    # > organize list
    elif args['list']:
        list_actions_and_filters()
    # > organize sim / run
    else:
        try:
            print(args)
            if args['<config_path>'] is not None:
              abs_path = Path(args['<config_path>'])
              print(abs_path)
              config = Config.from_file(abs_path)
            else:
              config = Config.from_file(config_path)
            execute_rules(config.rules, simulate=args['sim'])
        except Config.Error as e:
            logger.exception(e)
            print_error(e)
            puts("Try 'organize config --debug' for easier debugging.")
            puts('Full traceback at: %s' % log_path)
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print_error(e)
            puts('Full traceback at: %s' % log_path)
            sys.exit(1)


def config_edit():
    """ open the config file in $EDITOR or default text editor """
    editor = os.getenv('EDITOR')
    if editor:
        subprocess.call([editor, str(config_path)])
    else:
        open_in_filemanager(config_path)


def open_in_filemanager(path):
    """ opens the given path in file manager, using the default application """
    import webbrowser
    webbrowser.open(path.as_uri())


def config_debug():
    """ prints the config with resolved aliases, checks rules syntax and checks
        whether the given folders exist """
    haserr = False
    # check config syntax
    try:
        puts(bold('Your configuration as seen by the parser:'))
        with indent(2):
            config = Config.from_file(config_path)
            if not config.config:
                print_error('Config file is empty')
        puts(config.yaml())
        rules = config.rules
        puts('Config file syntax seems fine!')
    except Config.Error as e:
        haserr = True
        print_error(e)
    else:
        # check whether all folders exists:
        allfolders = set(flatten([rule.folders for rule in rules]))
        for f in allfolders:
            if not fullpath(f).exists():
                haserr = True
                puts(colored.yellow('Warning: "%s" does not exist!' % f))

    if not haserr:
        puts(colored.green('No config problems found.', bold=True))


def list_actions_and_filters():
    """ Prints a list of available actions and filters """
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


def print_error(text):
    puts('%s %s' % (colored.red('ERROR!', bold=True), text))
