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
  -F --format (default|errorsonly|JSONL)
                                  The output format [Default: default]
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
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from pydantic.functional_validators import BeforeValidator
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from typing_extensions import Annotated
from yaml.scanner import ScannerError

from organize import Config, ConfigError
from organize.find_config import ConfigNotFound, find_config, list_configs
from organize.output import JSONL, Default, Output

from .__version__ import __is_prerelease__, __version__

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
OutputFormat = Annotated[
    Literal["default", "jsonl", "errorsonly"], BeforeValidator(lambda v: v.lower())
]

console = Console()


def _open_uri(uri: str):
    import webbrowser

    webbrowser.open(uri)


def _output_for_format(format: OutputFormat) -> Output:
    if format == "default":
        return Default()
    elif format == "errorsonly":
        return Default(errors_only=True)
    elif format == "jsonl":
        return JSONL()
    raise ValueError(f"{format} is not a valid output format.")


def execute(
    config: Optional[str],
    working_dir: Optional[Path],
    format: OutputFormat,
    tags: Tags,
    skip_tags: Tags,
    simulate: bool,
) -> None:
    config_path = find_config(name_or_path=config)
    Config.from_path(config_path).execute(
        simulate=simulate,
        output=_output_for_format(format),
        tags=tags,
        skip_tags=skip_tags,
        working_dir=working_dir or Path("."),
    )


def new(config: Optional[str]) -> None:
    try:
        config_path = find_config(config)
        console.print(
            f'Config "{config_path}" already exists.\n'
            r'Use "organize new \[name]" to create a config in the default location.'
        )
    except ConfigNotFound as e:
        assert e.init_path is not None
        e.init_path.parent.mkdir(parents=True, exist_ok=True)
        e.init_path.write_text(EXAMPLE_CONFIG, encoding="utf-8")
        console.print(f'Config "{e.init_path.stem}" created at "{e.init_path}"')


def edit(config: Optional[str]) -> None:
    config_path = find_config(config)
    editor = os.getenv("EDITOR")
    if editor:
        os.system(f'{editor} "{config_path}"')
    else:
        _open_uri(config_path.as_uri())


def check(config: Optional[str]) -> None:
    config_path = find_config(config)
    Config.from_path(config_path=config_path)
    console.print(f'No problems found in "{config_path}".')


def debug(config: Optional[str]) -> None:
    from rich.pretty import pprint

    config_path = find_config(config)
    pprint(
        Config.from_path(config_path=config_path),
        expand_all=True,
        indent_guides=False,
    )


def show(config: Optional[str], path: bool, reveal: bool) -> None:
    config_path = find_config(name_or_path=config)
    if path:
        print(config_path)
    elif reveal:
        _open_uri(config_path.parent.as_uri())
    else:
        syntax = Syntax(config_path.read_text(encoding="utf-8"), "yaml")
        console.print(syntax)


def list_() -> None:
    table = Table()
    table.add_column("Config")
    table.add_column("Path", no_wrap=True, style="dim")
    for path in list_configs():
        table.add_row(path.stem, str(path))
    console.print(table)


def docs() -> None:
    uri = DOCS_GHPAGES if __is_prerelease__ else DOCS_RTD
    print(f'Opening "{uri}"')
    _open_uri(uri=uri)


class CliArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    config: Optional[str] = Field(..., alias="<config>")
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


def cli() -> None:
    arguments = docopt(
        __doc__,
        version=f"organize v{__version__}",
        default_help=True,
    )
    try:
        args = CliArgs.model_validate(arguments)
        _execute = partial(
            execute,
            config=args.config,
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
            new(config=args.config)
        elif args.edit:
            edit(config=args.config)
        elif args.check:
            check(config=args.config)
        elif args.debug:
            debug(config=args.config)
        elif args.show:
            show(config=args.config, path=args.path, reveal=args.reveal)
        elif args.list:
            list_()
        elif args.docs:
            docs()
    except (ConfigError, ConfigNotFound) as e:
        console.print(f"[red]Error: Config problem[/]\n{e}")
        sys.exit(1)
    except ValidationError as e:
        console.print(f"[red]Error: Invalid CLI arguments[/]\n{e}")
        sys.exit(2)
    except ScannerError as e:
        console.print(f"[red]Error: YAML syntax error[/]\n{e}")
        sys.exit(3)


if __name__ == "__main__":
    cli()
