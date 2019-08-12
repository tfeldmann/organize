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
import os
import sys
import logging

from clint.textui import colored, indent, puts
from docopt import docopt

from . import CONFIG_DIR, CONFIG_PATH, LOG_PATH
from . import __version__
from .core import execute_rules
from .config import Config
from .utils import Path, bold, flatten, fullpath

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
            puts(str(config_path))
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
            puts("Try 'organize config --debug' for easier debugging.")
            puts("Full traceback at: %s" % LOG_PATH)
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print_error(e)
            puts("Full traceback at: %s" % LOG_PATH)
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
    puts(str(config_path))
    haserr = False
    # check config syntax
    try:
        puts(bold("Your configuration as seen by the parser:"))
        with indent(2):
            config = Config.from_file(config_path)
            if not config.config:
                print_error("Config file is empty")
        puts(config.yaml())
        rules = config.rules
        puts("Config file syntax seems fine!")
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
        puts(colored.green("No config problems found.", bold=True))


def list_actions_and_filters():
    """ Prints a list of available actions and filters """
    import inspect
    from organize import filters, actions

    puts(bold("Filters:"))
    with indent(2):
        for name, _ in inspect.getmembers(filters, inspect.isclass):
            puts(name)
    puts()
    puts(bold("Actions:"))
    with indent(2):
        for name, _ in inspect.getmembers(actions, inspect.isclass):
            puts(name)


def print_error(text):
    puts("%s %s" % (colored.red("ERROR!", bold=True), text))
