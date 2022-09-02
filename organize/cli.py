"""
organize

The file management automation tool.
"""
import os
import sys
import textwrap
from typing import Optional, Tuple

import click
import fs

from . import console
from .__version__ import __version__
from .migration import NeedsMigrationError

DOCS_RTD = "https://organize.readthedocs.io"
DOCS_GHPAGES = "https://tfeldmann.github.io/organize/"

DEFAULT_CONFIG_FS_URL = "userconf://organize::/config.yaml"


def path_split(path_or_url: str) -> Tuple[str, str]:
    if sys.platform.startswith("win"):
        path_or_url = path_or_url.replace("\\", "/")
    dirname, filename = fs.path.split(path_or_url)
    return dirname, filename


def ensure_default_config():
    """
    Ensures a configuration file exists in the default location.
    """
    DEFAULT_CONFIG_TEXT = textwrap.dedent(
        """\
        # organize configuration file
        # {docs}

        rules:
          - name: "The name of this rule"
            locations:
              - # your locations here
            filters:
              - # your filters here
            actions:
              - # your actions here
        """
    ).format(docs=DOCS_RTD)

    dirname, filename = path_split(DEFAULT_CONFIG_FS_URL)
    if not filename:
        raise ValueError("invalid config path, missing filename")
    with fs.open_fs(dirname, create=True, writeable=True) as confdir:
        if not confdir.exists(filename):
            confdir.writetext(filename, DEFAULT_CONFIG_TEXT)


def config_path(fs_url: Optional[str] = None) -> Tuple[bool, str]:
    """
    Return the config path, resolved into a syspath if possible.
    If no fs_url is given, the default locations are checked.
    As last resort, a config is created in the default location.
    """
    is_syspath = False
    if not fs_url:
        # first check whether the user set a env var
        env_fs_url = os.getenv("ORGANIZE_CONFIG")
        if env_fs_url:
            fs_url = env_fs_url
        else:
            # if no env variable is given we make sure that there is a config file in
            # the default location
            ensure_default_config()
            fs_url = DEFAULT_CONFIG_FS_URL

    dirname, filename = path_split(fs_url)
    try:
        with fs.open_fs(dirname) as confdir:
            config_path = confdir.getsyspath(filename)
            is_syspath = True
    except Exception:
        config_path = fs_url
    return is_syspath, config_path


def read_config(fs_url: Optional[str] = None) -> Tuple[str, str]:
    """
    Read the config at the given fs_url.
    If no fs_url is given, try the default locations.
    """
    _, fs_url = config_path(fs_url)
    dirname, filename = path_split(fs_url)
    with fs.open_fs(dirname) as confdir:
        return (fs_url, confdir.readtext(filename))


class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()


class TagType(click.ParamType):
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
    from schema import SchemaError
    from . import core

    config_path, config_text = read_config(config)

    try:
        console.info(config=config_path, working_dir=working_dir)
        core.run(
            rules=config_text,
            simulate=simulate,
            working_dir=working_dir,
            tags=tags,
            skip_tags=skip_tags,
        )
    except NeedsMigrationError as e:
        from .migration import MIGRATION_DOCS_URL

        console.error(e, title="Config needs migration")
        console.warn(
            "Your config file needs some updates to work with organize v2.\n"
            "Please see the migration guide at\n\n"
            "%s" % MIGRATION_DOCS_URL
        )
        sys.exit(1)
    except SchemaError as e:
        console.error("Invalid config file!")
        for err in e.autos:
            if err and len(err) < 200:
                core.highlighted_console.print(err)
    except Exception as e:
        core.highlighted_console.print_exception()
    except (EOFError, KeyboardInterrupt):
        console.status.stop()
        console.warn("Aborted")


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
def edit(config: Optional[str], editor):
    """Edit the rules.

    If called without arguments it will open the default config file in $EDITOR.
    """
    is_syspath, confpath = config_path(config)
    if is_syspath:
        click.edit(filename=confpath, editor=editor)
    else:
        click.echo("Not a local config path: %s" % confpath)


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
        config_path, config_str = read_config(config)
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
@CLI_CONFIG
@click.option("--path", is_flag=True, help="Print the path instead of revealing it.")
def reveal(config: Optional[str], path: bool):
    """Reveals the default config file."""
    is_syspath, confpath = config_path(config)
    if path:
        click.echo(confpath)
        return
    try:
        # convert the url
        dirname, _ = path_split(confpath)
        import webbrowser

        with fs.open_fs(dirname) as dirfs:
            dir_url = dirfs.geturl("/")
            if not is_syspath:
                raise ValueError("not a local path")
            webbrowser.open(dir_url)
    except Exception as e:
        click.echo("Cannot reveal this config (%s)" % e)
        click.echo(confpath)


@cli.command()
def schema():
    """Prints the json schema for config files."""
    # ORGANIZE SCHEMA IS DEPRECATED AND WILL BE REMOVED IN THE FUTURE
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
    import webbrowser

    webbrowser.open(DOCS_RTD)


if __name__ == "__main__":
    cli()
