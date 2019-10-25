"""
organize -- The file management automation tool.

Usage:
    organize sim [--config-file=<path>]
    organize run [--config-file=<path>]
    organize config [--open-folder | --path | --debug] [--config-file=<path>]
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
import os
import sys

from colorama import Fore, Style
from docopt import docopt

from . import CONFIG_DIR, CONFIG_PATH, LOG_PATH
from .__version__ import __version__
from .compat import Path
from .config import Config
from .core import execute_rules
from .utils import flatten, fullpath

logger = logging.getLogger("organize")


def main(argv=None):
    """ entry point for the command line interface """
    args = docopt(__doc__, argv=argv, version=__version__, help=True)

    # override default config file path
    if args["--config-file"]:
        config_path = Path(args["--config-file"]).resolve()
        config_dir = config_path.parent
    else:
        config_dir = CONFIG_DIR
        config_path = CONFIG_PATH

    # > organize config
    if args["config"]:
        if args["--open-folder"]:
            open_in_filemanager(config_dir)
        elif args["--path"]:
            print(str(config_path))
        elif args["--debug"]:
            config_debug(config_path)
        else:
            config_edit(config_path)

    # > organize list
    elif args["list"]:
        list_actions_and_filters()

    # > organize sim / run
    else:
        try:
            config = Config.from_file(config_path)
            execute_rules(config.rules, simulate=args["sim"])
        except Config.Error as e:
            logger.exception(e)
            print_error(e)
            print("Try 'organize config --debug' for easier debugging.")
            print("Full traceback at: %s" % LOG_PATH)
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print_error(e)
            print("Full traceback at: %s" % LOG_PATH)
            sys.exit(1)


def config_edit(config_path):
    """ open the config file in $EDITOR or default text editor """
    # attention: the env variable might contain command line arguments.
    # https://github.com/tfeldmann/organize/issues/24
    editor = os.getenv("EDITOR")
    if editor:
        os.system('%s "%s"' % (editor, config_path))
    else:
        open_in_filemanager(config_path)


def open_in_filemanager(path):
    """ opens the given path in file manager, using the default application """
    import webbrowser

    webbrowser.open(path.as_uri())


def config_debug(config_path):
    """ prints the config with resolved yaml aliases, checks rules syntax and checks
        whether the given folders exist
    """
    print(str(config_path))
    haserr = False
    # check config syntax
    try:
        print(Style.BRIGHT + "Your configuration as seen by the parser:")
        config = Config.from_file(config_path)
        if not config.config:
            print_error("Config file is empty")
            return
        print(config.yaml())
        rules = config.rules
        print("Config file syntax seems fine!")
    except Config.Error as e:
        haserr = True
        print_error(e)
    else:
        # check whether all folders exists:
        allfolders = set(flatten([rule.folders for rule in rules]))
        for f in allfolders:
            if not fullpath(f).exists():
                haserr = True
                print(Fore.YELLOW + 'Warning: "%s" does not exist!' % f)

    if not haserr:
        print(Fore.GREEN + Style.BRIGHT + "No config problems found.")


def list_actions_and_filters():
    """ Prints a list of available actions and filters """
    import inspect
    from organize import filters, actions

    print(Style.BRIGHT + "Filters:")
    for name, _ in inspect.getmembers(filters, inspect.isclass):
        print("  " + name)
    print()
    print(Style.BRIGHT + "Actions:")
    for name, _ in inspect.getmembers(actions, inspect.isclass):
        print("  " + name)


def print_error(e):
    print(Style.BRIGHT + Fore.RED + "ERROR:" + Style.RESET_ALL + " %s" % e)
