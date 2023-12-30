__doc__ = """
organize - The file management automation tool.

Usage:
  organize run   [options] [<config>]
  organize sim   [options] [<config>]
  organize new   [<config>]
  organize edit  [<config>]
  organize check [<config>]
  organize debug [<config>]
  organize show  [--path|--reveal] [<config>]
  organize list
  organize docs
  organize --version
  organize --help

Commands:
  run        Organize your files.
  sim        Simulate organizing your files.
  new        Creates a default config.
  edit       Edit the config file with $EDITOR
  check      Check config file validity
  debug      Shows the raw config parsing steps.
  show       Print the config to stdout.
               Use --reveal to reveal the file in your file manager
               Use --path to show the path to the file
  list       Lists config files found in the default locations.
  docs       Open the documentation.

Options:
  <config>                        A config name or path to a config file
  -W --working-dir <dir>          The working directory
  -F --format (default|jsonl)     The output format [Default: default]
  -T --tags <tags>                Tags to run (eg. "initial,release")
  -S --skip-tags <tags>           Tags to skip
  -h --help                       Show this help page.
"""
import os
import sys
from functools import partial
from pathlib import Path
from typing import Literal, Optional, Set

from docopt import docopt
from pydantic import BaseModel, Field, ValidationError, field_validator
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from organize import Config, ConfigError
from organize.find_config import ConfigNotFound, find_config, list_configs
from organize.output import JSONL, Default

from .__version__ import __version__

DOCS_RTD = "https://organize.readthedocs.io"
DOCS_GHPAGES = "https://tfeldmann.github.io/organize/"

EXAMPLE_CONFIG = f"""\
# organize configuration file
# {DOCS_RTD}

rules:
  - locations:
    filters:
    actions:
      - echo: "Hello, World!"
"""

Tags = Set[str]
OutputFormat = Literal["default", "jsonl"]

console = Console()


def _open_uri(uri: str):
    import webbrowser

    webbrowser.open(uri)


def execute(
    config: str,
    working_dir: Optional[Path],
    format: OutputFormat,
    tags: Tags,
    skip_tags: Tags,
    simulate: bool,
):
    output = JSONL() if format == "jsonl" else Default()
    config_path = find_config(name_or_path=config)
    Config.from_path(config_path).execute(
        simulate=simulate,
        output=output,
        tags=tags,
        skip_tags=skip_tags,
        working_dir=working_dir or Path("."),
    )


def new(config: str):
    try:
        config_path = find_config(config)
        console.print(
            f'Config "{config_path}" already exists.\n'
            'Use "organize new \[name]" to create a config in the default location.'
        )
    except ConfigNotFound as e:
        assert e.init_path is not None
        e.init_path.write_text(EXAMPLE_CONFIG)
        console.print(f'Config "{e.init_path.stem}" created at "{e.init_path}"')


def edit(config: str):
    config_path = find_config(config)
    editor = os.getenv("EDITOR")
    if editor:
        os.system(f'{editor} "{config_path}"')
    else:
        _open_uri(config_path.as_uri())


def check(config: str):
    config_path = find_config(config)
    Config.from_path(config_path=config_path)
    console.print(f'No problems found in "{config_path}".')


def debug(config: str):
    from rich.pretty import pprint

    config_path = find_config(config)
    pprint(
        Config.from_path(config_path=config_path),
        expand_all=True,
        indent_guides=False,
    )


def show(config: str, path: bool, reveal: bool):
    config_path = find_config(name_or_path=config)
    if path:
        print(config_path)
    elif reveal:
        _open_uri(config_path.parent.as_uri())
    else:
        syntax = Syntax(config_path.read_text(), "yaml")
        console.print(syntax)


def list_():
    table = Table()
    table.add_column("Config")
    table.add_column("Path", no_wrap=True, style="dim")
    for path in list_configs():
        table.add_row(path.stem, str(path))
    console.print(table)


def docs():
    print(f'Opening "{DOCS_RTD}"')
    _open_uri(uri=DOCS_RTD)


class CliArgs(BaseModel, extra="forbid"):
    # commands
    run: bool
    sim: bool
    new: bool
    edit: bool
    check: bool
    debug: bool
    show: bool
    list: bool
    docs: bool

    # run / sim options
    config_name: Optional[str] = Field(..., alias="<config>")
    working_dir: Optional[Path] = Field(..., alias="--working-dir")
    format: OutputFormat = Field("default", alias="--format")
    tags: Optional[str] = Field(..., alias="--tags")
    skip_tags: Optional[str] = Field(..., alias="--skip-tags")

    # show options
    path: bool = Field(False, alias="--path")
    reveal: bool = Field(False, alias="--reveal")

    # docopt options
    version: bool = Field(..., alias="--version")
    help: bool = Field(..., alias="--help")

    @field_validator("tags", "skip_tags", mode="after")
    @classmethod
    def split_tags(cls, val) -> Set[str]:
        if val is None:
            return set()
        return set(val.split(","))


def cli():
    from rich import print

    arguments = docopt(
        __doc__,
        version=f"organize v{__version__}",
        default_help=True,
    )
    try:
        args = CliArgs.model_validate(arguments)
        _execute = partial(
            execute,
            config=args.config_name,
            working_dir=args.working_dir,
            format=args.format,
            tags=args.tags,
            skip_tags=args.skip_tags,
        )
        if args.run:
            _execute(simulate=False)
        elif args.sim:
            _execute(simulate=True)
        elif args.new:
            new(config=args.config_name)
        elif args.edit:
            edit(config=args.config_name)
        elif args.check:
            check(config=args.config_name)
        elif args.debug:
            debug(config=args.config_name)
        elif args.show:
            show(config=args.config_name, path=args.path, reveal=args.reveal)
        elif args.list:
            list_()
        elif args.docs:
            docs()
    except (ConfigError, ConfigNotFound) as e:
        print(e)
        sys.exit(1)
    except ValidationError as e:
        print(e)
        sys.exit(2)


if __name__ == "__main__":
    cli()
