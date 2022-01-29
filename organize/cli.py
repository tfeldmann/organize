import click
from . import CONFIG_DIR, CONFIG_PATH, LOG_PATH
from .__version__ import __version__
from .config import CONFIG_SCHEMA
from .output import console

import os
import appdirs
from pathlib import Path

# prepare config and log folders
APP_DIRS = appdirs.AppDirs("organize")

# setting the $ORGANIZE_CONFIG env variable overrides the default config path
if os.getenv("ORGANIZE_CONFIG"):
    CONFIG_PATH = Path(os.getenv("ORGANIZE_CONFIG", "")).resolve()
    CONFIG_DIR = CONFIG_PATH.parent
else:
    CONFIG_DIR = Path(APP_DIRS.user_config_dir)
    CONFIG_PATH = CONFIG_DIR / "config.yaml"


class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()


CLI_RULES_FILE = click.argument(
    "rule_file",
    required=False,
    envvar="ORGANIZE_RULE_FILE",
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


def warn(msg):
    console.print("Warning: %s" % msg, style="yellow")


@click.group(
    cls=NaturalOrderGroup,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(__version__)
def cli():
    """
    organize

    The file management automation tool.
    """
    pass


@cli.command()
@CLI_RULES_FILE
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
def run(rule_file, working_dir, config_file):
    """Organizes your files according to your rules."""
    print(rule_file, working_dir, config_file)


@cli.command()
@CLI_RULES_FILE
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
def sim(rule_file, working_dir, config_file):
    """Simulates a run (does not touch your files)."""
    print(rule_file, working_dir, config_file)


@cli.group()
def rules():
    """Manage your rules"""
    pass


@rules.command()
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
    """Edit a rule file.

    If called without further arguments, it will open the default rule file in $EDITOR.
    """
    click.edit(filename=rule_file, editor=editor)


@rules.command()
@CLI_RULES_FILE
def check(rule_file):
    """Checks whether the given rule file is valid"""
    print(rule_file)


@rules.command()
def schema():
    """Checks whether the given rule file is valid"""
    import json

    js = json.dumps(
        CONFIG_SCHEMA.json_schema(
            schema_id="https://tfeldmann.de/organize.schema.json",
        )
    )
    console.print_json(js)


@rules.command()
def path():
    """Prints the path of the default rule file"""
    click.echo(CONFIG_PATH)


@rules.command()
def reveal():
    """Reveals the default rule file"""
    click.launch(str(CONFIG_PATH), locate=True)


@cli.command(hidden=True)
@click.option("--path", is_flag=True, help="Print the default config file path")
@click.option("--debug", is_flag=True, help="Debug the default config file")
@click.option("--open-folder", is_flag=True)  # backwards compatibility
@click.pass_context
def config(ctx, path, debug, open_folder):
    """Edit the default configuration file."""
    warn("`organize config` is deprecated. Please try the new `organize rules`.")
    if open_folder:
        ctx.invoke(reveal)
    elif path:
        ctx.invoke(path)
    elif debug:
        ctx.invoke(check)
    else:
        ctx.invoke(edit)


@cli.command(help="Open the documentation")
def docs():
    click.launch("https://organize.readthedocs.io")


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


# def config_edit(config_path: Path) -> None:
#     """open the config file in $EDITOR or default text editor"""
#     # attention: the env variable might contain command line arguments.
#     # https://github.com/tfeldmann/organize/issues/24
#     editor = os.getenv("EDITOR")
#     if editor:
#         os.system('%s "%s"' % (editor, config_path))
#     else:
#         open_in_filemanager(config_path)


# def open_in_filemanager(path: Path) -> None:
#     """opens the given path in file manager, using the default application"""
#     import webbrowser  # pylint: disable=import-outside-toplevel

#     webbrowser.open(path.as_uri())


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
