"""
organize

The file management automation tool.
"""
import os
import sys
from pathlib import Path
from typing import Tuple, Optional

import click
from fs import appfs

from . import console
from .__version__ import __version__
from .migration import NeedsMigrationError

# alternative docs url: "https://tfeldmann.github.io/organize/"
DOCS_URL = "https://organize.readthedocs.io"
MIGRATE_URL = "https://organize.readthedocs.io/en/latest/updating-from-v1/"
DEFAULT_CONFIG = """\
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
""".format(
    docs=DOCS_URL
)

try:
    config_filename = "config.yaml"
    envvar = os.getenv("ORGANIZE_CONFIG")
    if envvar:
        dirname, config_filename = os.path.split(envvar)
        if not dirname or not config_filename:
            raise ValueError("Invalid ORGANIZE_CONFIG: %s" % envvar)
        CONFIG_PATH = Path(envvar)
    else:
        CONFIG_PATH = Path(appfs.UserConfigFS("organize").getsyspath(config_filename))

    # create default config file if it not exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(DEFAULT_CONFIG)
except Exception as e:
    console.error(str(e), title="Config file")
    sys.exit(1)


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
    default=CONFIG_PATH,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
CLI_WORKING_DIR_OPTION = click.option(
    "--working-dir",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="The working directory",
)
# for CLI backwards compatibility with organize v1.x
CLI_CONFIG_FILE_OPTION = click.option(
    "--config-file",
    default=None,
    hidden=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
CLI_TAGS = click.option("--tags", type=TagType(), default="")
CLI_SKIP_TAGS = click.option("--skip-tags", type=TagType(), default="")


def run_local(
    config_path: Path,
    working_dir: str,
    simulate: bool,
    tags: Optional[Tuple[str]] = None,
    skip_tags: Optional[Tuple[str]] = None,
):
    from schema import SchemaError

    from . import core

    try:
        console.info(config_path=config_path, working_dir=working_dir)
        config = config_path.read_text()
        core.run(
            rules=config,
            simulate=simulate,
            working_dir=working_dir,
            tags=tags,
            skip_tags=skip_tags,
        )
    except NeedsMigrationError as e:
        console.error(e, title="Config needs migration")
        console.warn(
            "Your config file needs some updates to work with organize v2.\n"
            "Please see the migration guide at\n\n"
            "%s" % MIGRATE_URL
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
@CLI_CONFIG_FILE_OPTION
@CLI_TAGS
@CLI_SKIP_TAGS
def run(config: Path, working_dir: Path, config_file, tags, skip_tags):
    """Organizes your files according to your rules."""
    if config_file:
        config = config_file
        console.deprecated(
            "The --config-file option can now be omitted. See organize --help."
        )
    run_local(
        config_path=config,
        working_dir=working_dir,
        simulate=False,
        tags=tags,
        skip_tags=skip_tags,
    )


@cli.command()
@CLI_CONFIG
@CLI_WORKING_DIR_OPTION
@CLI_CONFIG_FILE_OPTION
@CLI_TAGS
@CLI_SKIP_TAGS
def sim(config: Path, working_dir: Path, config_file, tags, skip_tags):
    """Simulates a run (does not touch your files)."""
    if config_file:
        config = config_file
        console.deprecated(
            "The --config-file option can now be omitted. See organize --help."
        )
    run_local(
        config_path=config,
        working_dir=working_dir,
        simulate=True,
        tags=tags,
        skip_tags=skip_tags,
    )


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
@click.option("--debug", is_flag=True, help="Verbose output")
def check(config: Path, debug):
    """Checks whether a given config file is valid.

    If called without arguments it will check the default config file.
    """
    from . import migration
    from .config import cleanup, load_from_string, validate
    from .core import highlighted_console as out
    from .core import replace_with_instances

    print("Checking: %s" % config)
    try:
        config_str = config.read_text()

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
