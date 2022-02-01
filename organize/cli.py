"""
organize

The file management automation tool.
"""
import os
import sys

import click
from fs import appfs, osfs

from . import console
from .__version__ import __version__

DOCS_URL = "https://tfeldmann.github.io/organize/"  # "https://organize.readthedocs.io"
DEFAULT_CONFIG = """\
# organize configuration file
# {docs}

rules:
  - locations:
      -
    filters:
      -
    actions:
      -
""".format(
    docs=DOCS_URL
)

try:
    config_filename = "config.yaml"
    if os.getenv("ORGANIZE_CONFIG"):
        dirname, config_filename = os.path.split(os.getenv("ORGANIZE_CONFIG", ""))
        config_fs = osfs.OSFS(dirname, create=False)
    else:
        config_fs = appfs.UserConfigFS("organize", create=True)

    # create default config file if it not exists
    if not config_fs.exists(config_filename):
        config_fs.writetext(config_filename, DEFAULT_CONFIG)
    CONFIG_PATH = config_fs.getsyspath(config_filename)
except Exception as e:
    console.error(str(e), title="Config file")
    sys.exit(1)


class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()


CLI_CONFIG = click.argument(
    "config",
    required=False,
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
@CLI_CONFIG
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
def run(config, working_dir, config_file):
    """Organizes your files according to your rules."""
    from .core import run_file

    if config_file:
        config = config_file
        console.deprecated(
            "The --config-file option can now be omitted. See organize --help."
        )
    run_file(config_file=config, working_dir=working_dir, simulate=False)


@cli.command()
@CLI_CONFIG
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
def sim(config, working_dir, config_file):
    """Simulates a run (does not touch your files)."""
    from .core import run_file

    if config_file:
        config = config_file
        console.deprecated(
            "The --config-file option can now be omitted. See organize --help."
        )
    run_file(config_file=config, working_dir=working_dir, simulate=True)


@cli.command()
@click.argument(
    "config",
    required=False,
    default=CONFIG_PATH,
    type=click.Path(),
)
@click.option(
    "--editor",
    envvar="EDITOR",
    help="The editor to use. (Default: $EDITOR)",
)
def edit(config, editor):
    """Edit the rules.

    If called without arguments it will open the default config file in $EDITOR.
    """
    click.edit(filename=config, editor=editor)


@cli.command()
@CLI_CONFIG
def check(config):
    """Checks whether a given config file is valid.

    If called without arguments it will check the default config file.
    """
    print(config)


@cli.command()
@click.option("--path", is_flag=True, help="Print the path instead of revealing it.")
def reveal(path):
    """Reveals the default config file."""
    if path:
        click.echo(CONFIG_PATH)
    else:
        click.launch(str(CONFIG_PATH), locate=True)


@cli.command()
def schema():
    """Prints the json schema for config files."""
    import json

    from .config import CONFIG_SCHEMA
    from .console import console as richconsole

    js = json.dumps(
        CONFIG_SCHEMA.json_schema(
            schema_id="https://tfeldmann.de/organize.schema.json",
        )
    )
    richconsole.print_json(js)


@cli.command()
def docs():
    """Opens the documentation."""
    click.launch(DOCS_URL)


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
    console.deprecated("`organize config` is deprecated.")
    console.deprecated("Please see `organize --help` for all available commands.")


if __name__ == "__main__":
    cli()
