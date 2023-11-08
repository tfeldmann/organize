"""
organize

The file management automation tool.
"""
import os
import sys
import textwrap
from pathlib import Path
from typing import Optional, Tuple

import click
import platformdirs

from organize import Config
from organize.utils import expandvars

from .__version__ import __version__

DOCS_RTD = "https://organize.readthedocs.io"
DOCS_GHPAGES = "https://tfeldmann.github.io/organize/"


def find_config(name_or_path: Optional[str] = None) -> Path:
    USER_CONFIG_DIR = platformdirs.user_config_path(appname="organize")

    if name_or_path is None:
        ORGANIZE_CONFIG = os.environ.get("ORGANIZE_CONFIG")
        if ORGANIZE_CONFIG is not None:
            # if the `ORGANIZE_CONFIG` env variable is defined we only check this
            # specific location
            return expandvars(ORGANIZE_CONFIG)
        # no name and no ORGANIZE_CONFIG env variable given:
        # -> check only the default config
        return USER_CONFIG_DIR / "config.yaml"

    XDG_CONFIG_HOME = (
        expandvars(os.environ.get("XDG_CONFIG_HOME", "~/.config")) / "organize"
    )

    # otherwise we try:
    # 1.`$PWD`
    # 2. the platform specifig config dir
    # 3. `$XDG_CONFIG_HOME/organize`
    as_path = expandvars(name_or_path)
    if as_path.exists():
        return as_path

    if not as_path.is_absolute():
        as_yml = as_path.with_suffix(".yml")
        as_yaml = as_path.with_suffix(".yaml")
        pathes = (
            as_yaml,
            as_yml,
            USER_CONFIG_DIR / as_path,
            USER_CONFIG_DIR / as_yaml,
            USER_CONFIG_DIR / as_yml,
            XDG_CONFIG_HOME / as_path,
            XDG_CONFIG_HOME / as_yaml,
            XDG_CONFIG_HOME / as_yml,
        )
        for path in pathes:
            if path.exists():
                return path
    raise FileNotFoundError(f'Config "{name_or_path}" not found.')


def ensure_default_config():
    """
    Ensures a configuration file exists in the default location.
    """
    DEFAULT_CONFIG_TEXT = textwrap.dedent(
        """\
        # organize configuration file
        # {docs}

        rules:
          - locations:
            filters:
            actions:
              - echo: "Hello, World!"
        """
    ).format(docs=DOCS_RTD)

    dirname, filename = path_split(DEFAULT_CONFIG_FS_URL)
    if not filename:
        raise ValueError("invalid config path, missing filename")
    with fs.open_fs(dirname, create=True, writeable=True) as confdir:
        if not confdir.exists(filename):
            confdir.writetext(filename, DEFAULT_CONFIG_TEXT)


class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()


class TagType(click.ParamType):
    """Support comma separated tags"""

    name = "tag"

    def convert(self, value, param, ctx):
        if not value:
            return tuple()
        return tuple(tag.strip() for tag in value.split(","))


CLI_CONFIG = click.argument(
    "config",
    required=False,
    type=str,
)
CLI_WORKING_DIR_OPTION = click.option(
    "--working-dir",
    default="",
    type=str,
    help="The working directory",
)
CLI_TAGS = click.option(
    "--tags",
    type=TagType(),
    default="",
    help="tags to run",
)
CLI_SKIP_TAGS = click.option(
    "--skip-tags",
    type=TagType(),
    default="",
    help="tags to skip",
)


def execute(
    config: Optional[str],
    working_dir: str,
    simulate: bool,
    tags: Optional[Tuple[str]] = None,
    skip_tags: Optional[Tuple[str]] = None,
):
    config_path = find_config(config)
    Config.from_path(config_path).execute(
        simulate=simulate,
        working_dir=working_dir,
        tags=tags,
        skip_tags=skip_tags,
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
@CLI_TAGS
@CLI_SKIP_TAGS
def run(config: Optional[str], working_dir: str, tags, skip_tags):
    """Organizes your files according to your rules."""
    execute(
        config=config,
        working_dir=working_dir,
        simulate=False,
        tags=tags,
        skip_tags=skip_tags,
    )


@cli.command()
@CLI_CONFIG
@CLI_WORKING_DIR_OPTION
@CLI_TAGS
@CLI_SKIP_TAGS
def sim(config: Optional[str], working_dir: str, tags, skip_tags):
    """Simulates a run (does not touch your files)."""
    execute(
        config=config,
        working_dir=working_dir,
        simulate=True,
        tags=tags,
        skip_tags=skip_tags,
    )


@cli.command()
@click.argument("config", required=False, type=str)
@click.option(
    "--editor",
    envvar="EDITOR",
    help="The editor to use. (Default: $EDITOR)",
)
def edit(config, editor):
    """Edit the rules.

    If called without arguments it will open the default config file in $EDITOR.
    """
    config_path = find_config(config)
    click.edit(filename=str(config_path), editor=editor)


@cli.command()
@CLI_CONFIG
@click.option("--debug", is_flag=True, help="Verbose output")
def check(config: str, debug):
    """Checks whether a given config file is valid.

    If called without arguments it will check the default config file.
    """
    from . import migration
    from .config import cleanup, load_from_string, validate
    from .core import highlighted_console as out
    from .core import replace_with_instances

    try:
        if config:
            config_path, config_str = read_config(config)
        else:
            config_path, config_str = read_default_config()
        print("Checking: %s" % config_path)

        if debug:
            out.rule("Raw", align="left")
            out.print(config_str)

        rules = load_from_string(config_str)

        if debug:
            out.print("\n\n")
            out.rule("Loaded", align="left")
            out.print(rules)

        rules = cleanup(rules)

        if debug:
            out.print("\n\n")
            out.rule("Cleaned", align="left")
            out.print(rules)

        if debug:
            out.print("\n\n")
            out.rule("Migration from v1", align="left")

        migration.migrate_v1(rules)

        if debug:
            out.print("Not needed.")
            out.print("\n\n")
            out.rule("Schema validation", align="left")

        validate(rules)

        if debug:
            out.print("Validation ok.")
            out.print("\n\n")
            out.rule("Instantiation", align="left")

        # warnings = replace_with_instances(rules)
        # if debug:
        #     out.print(rules)
        #     for msg in warnings:
        #         out.print("Warning: %s" % msg)

        if debug:
            out.print("\n\n")
            out.rule("Result", align="left")
        out.print("Config is valid.")

    except Exception as e:
        out.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--path", is_flag=True, help="Print the path instead of revealing it.")
def reveal(path: bool):
    config_path = find_config(name_or_path=None)
    if path:
        print(f"{config_path}")
    else:
        import webbrowser

        webbrowser.open(config_path.parent.as_uri())


@cli.command()
def docs():
    """Opens the documentation."""
    import webbrowser

    webbrowser.open(DOCS_RTD)


if __name__ == "__main__":
    cli()
