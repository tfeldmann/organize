"""
organize

The file management automation tool.
"""
import os
from pathlib import Path

import appdirs
import click

from .__version__ import __version__
from .output import console, warn

# prepare config and log folders
APP_DIRS = appdirs.AppDirs("organize")

# setting the $ORGANIZE_CONFIG env variable overrides the default config path
if os.getenv("ORGANIZE_CONFIG"):
    CONFIG_PATH = Path(os.getenv("ORGANIZE_CONFIG", "")).resolve()
    CONFIG_DIR = CONFIG_PATH.parent
else:
    CONFIG_DIR = Path(APP_DIRS.user_config_dir)
    CONFIG_PATH = CONFIG_DIR / "config.yaml"

LOG_DIR = Path(APP_DIRS.user_log_dir)
LOG_PATH = LOG_DIR / "organize.log"

for folder in (CONFIG_DIR, LOG_DIR):
    folder.mkdir(parents=True, exist_ok=True)

# create empty config file if it does not exist
if not CONFIG_PATH.exists():
    CONFIG_PATH.touch()


class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()


CLI_RULES_FILE = click.argument(
    "rule_file",
    required=False,
    envvar="ORGANIZE_RULE_FILE",
    default=CONFIG_PATH,
    type=click.Path(exists=True),
)
CLI_WORKING_DIR_OPTION = click.option(
    "--working-dir",
    default=".",
    type=click.Path(exists=True),
    help="The working directory",
)
# for CLI backwards compatibility with organize v1.x
CLI_CONFIG_FILE_OPTION = click.option(
    "--config-file",
    envvar="ORGANIZE_CONFIG",
    default=None,
    hidden=True,
    type=click.Path(exists=True),
)


@click.group(
    help=__doc__,
    cls=NaturalOrderGroup,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(__version__)
def cli():
    pass


@cli.command()
@CLI_RULES_FILE
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
def run(rule_file, working_dir, config_file):
    """Organizes your files according to your rules."""
    from .core import run_file

    if config_file and not rule_file:
        rule_file = config_file
    run_file(rule_file=rule_file, working_dir=working_dir, simulate=False)


@cli.command()
@CLI_RULES_FILE
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
def sim(rule_file, working_dir, config_file):
    """Simulates a run (does not touch your files)."""
    from .core import run_file

    if config_file and not rule_file:
        rule_file = config_file
    run_file(rule_file=rule_file, working_dir=working_dir, simulate=True)


@cli.command()
@click.argument(
    "rule_file",
    required=False,
    default=CONFIG_PATH,
    envvar="ORGANIZE_RULE_FILE",
    type=click.Path(),
)
@click.option(
    "--editor",
    envvar="EDITOR",
    help="The editor to use. (Default: $EDITOR)",
)
def edit(rule_file, editor):
    """Edit the rules.

    If called without arguments, it will open the default rule file in $EDITOR.
    """
    click.edit(filename=rule_file, editor=editor)


@cli.command()
@CLI_RULES_FILE
def check(rule_file):
    """Checks whether a given rule file is valid.

    If called without arguments, it will check the default rule file
    """
    print(rule_file)


@cli.command()
@click.option("--path", is_flag=True, help="Print the path instead of revealing it.")
def reveal(path):
    """Reveals the default rule file."""
    if path:
        click.echo(CONFIG_PATH)
    else:
        click.launch(str(CONFIG_PATH), locate=True)


@cli.command()
def schema():
    """Prints the json schema for rule files."""
    import json

    from .config import CONFIG_SCHEMA

    js = json.dumps(
        CONFIG_SCHEMA.json_schema(
            schema_id="https://tfeldmann.de/organize.schema.json",
        )
    )
    console.print_json(js)


@cli.command()
def docs():
    """Opens the documentation."""
    click.launch("https://organize.readthedocs.io")


# deprecated - only here for backwards compatibility
@cli.command(hidden=True)
@click.option("--path", is_flag=True, help="Print the default config file path")
@click.option("--debug", is_flag=True, help="Debug the default config file")
@click.option("--open-folder", is_flag=True)
@click.pass_context
def config(ctx, path, debug, open_folder):
    """Edit the default configuration file."""
    if open_folder:
        ctx.invoke(reveal)
    elif path:
        ctx.invoke(reveal, path=True)
        return
    elif debug:
        ctx.invoke(check)
    else:
        ctx.invoke(edit)
    warn("`organize config` is deprecated.")
    warn("Please see `organize --help` for all available commands.")


if __name__ == "__main__":
    cli()


# def main(argv=None):
#     """entry point for the command line interface"""
#     args = docopt(__doc__, argv=argv, version=__version__, help=True)

#     # override default config file path
#     if args["--config-file"]:
#         expanded_path = os.path.expandvars(args["--config-file"])
#         config_path = Path(expanded_path).expanduser().resolve()
#         config_dir = config_path.parent
#     else:
#         config_dir = CONFIG_DIR
#         config_path = CONFIG_PATH

#     # > organize config
#     if args["config"]:
#         if args["--open-folder"]:
#             open_in_filemanager(config_dir)
#         elif args["--path"]:
#             print(str(config_path))
#         elif args["--debug"]:
#             config_debug(config_path)
#         else:
#             config_edit(config_path)

#     # > organize list
#     elif args["list"]:
#         list_actions_and_filters()

#     # > organize sim / run
#     else:
#         try:
#             config = Config.from_file(config_path)
#             execute_rules(config.rules, simulate=args["sim"])
#         except Config.Error as e:
#             logger.exception(e)
#             print_error(e)
#             print("Try 'organize config --debug' for easier debugging.")
#             print("Full traceback at: %s" % LOG_PATH)
#             sys.exit(1)
#         except Exception as e:  # pylint: disable=broad-except
#             logger.exception(e)
#             print_error(e)
#             print("Full traceback at: %s" % LOG_PATH)
#             sys.exit(1)


# def config_debug(config_path: Path) -> None:
#     """prints the config with resolved yaml aliases, checks rules syntax and checks
#     whether the given folders exist
#     """
#     print(str(config_path))
#     haserr = False
#     # check config syntax
#     try:
#         print(Style.BRIGHT + "Your configuration as seen by the parser:")
#         config = Config.from_file(config_path)
#         if not config.config:
#             print_error("Config file is empty")
#             return
#         print(config.yaml())
#         rules = config.rules
#         print("Config file syntax seems fine!")
#     except Config.Error as e:
#         haserr = True
#         print_error(e)
#     else:
#         # check whether all folders exists:
#         allfolders = set(flatten([rule.folders for rule in rules]))
#         for f in allfolders:
#             if not fullpath(f).exists():
#                 haserr = True
#                 print(Fore.YELLOW + 'Warning: "%s" does not exist!' % f)

#     if not haserr:
#         print(Fore.GREEN + Style.BRIGHT + "No config problems found.")


# def list_actions_and_filters() -> None:
#     """Prints a list of available actions and filters"""
#     import inspect  # pylint: disable=import-outside-toplevel

#     from organize import actions, filters  # pylint: disable=import-outside-toplevel

#     print(Style.BRIGHT + "Filters:")
#     for name, _ in inspect.getmembers(filters, inspect.isclass):
#         print("  " + name)
#     print()
#     print(Style.BRIGHT + "Actions:")
#     for name, _ in inspect.getmembers(actions, inspect.isclass):
#         print("  " + name)


# def print_error(e: Union[Exception, str]) -> None:
#     print(Style.BRIGHT + Fore.RED + "ERROR:" + Style.RESET_ALL + " %s" % e)
