__doc__ = """
organize - The file management automation tool.

Usage:
  organize run [options] [<config>]
  organize sim [options] [<config>]
  organize config (init|edit|check|debug|path|reveal) [<config>]
  organize docs
  organize --version
  organize --help

Commands:
  run        Organize your files.
  sim        Simulate organizing your files.
  config     Do something with your config file:
    init       Creates a default config.
    edit       Edit the config file with $EDITOR
    check      Check config file validity
    debug      Shows the raw config parsing steps.
    path       Print the full path to the config file
    reveal     Reveal the config file in your file manager.
  docs       Open the documentation.

Options:
  <config>                        A config name or path to a config file
  -w --working-dir <dir>          The working directory
  -f --format (default|jsonl)     The output format [Default: default]
  --tags <tags>                   tags to run (eg. "initial,release")
  --skip-tags <tags>              tags to skip
  -h --help                       Show this help page.
"""
import os
import sys
from functools import partial
from pathlib import Path
from typing import Literal, Optional, Set

from docopt import docopt
from pydantic import BaseModel, Field, field_validator

from organize import Config, ConfigError
from organize.find_config import ConfigNotFound, find_config
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
        working_dir=working_dir,
    )


def config_init(config: str):
    try:
        config_path = find_config(config)
        raise FileExistsError(f'Config "{config_path} already exists.')
    except ConfigNotFound as e:
        assert e.init_path is not None
        e.init_path.write_text(EXAMPLE_CONFIG)
        print(f'Config created at "{e.init_path}"')


def config_edit(config: str):
    config_path = find_config(config)
    editor = os.getenv("EDITOR")
    if editor:
        os.system(f'{editor} "{config_path}"')
    else:
        _open_uri(config_path.as_uri())


def config_check(config: str):
    config_path = find_config(config)
    print(config_path)
    Config.from_path(config_path=config_path)
    print(f'No problems found in "{config_path}".')


def config_debug(config: str):
    from rich.pretty import pprint

    config_path = find_config(config)
    pprint(
        Config.from_path(config_path=config_path),
        expand_all=True,
        indent_guides=False,
    )


def config_path(config: str):
    print(find_config(name_or_path=config))


def config_reveal(config: str):
    config_path = find_config(name_or_path=config)
    _open_uri(config_path.parent.as_uri())


def docs():
    print(f'Opening "{DOCS_RTD}"')
    _open_uri(uri=DOCS_RTD)


class CliArgs(BaseModel, extra="forbid"):
    # commands
    run: bool
    sim: bool
    config: bool
    docs: bool

    # config subcommands
    init: bool
    edit: bool
    check: bool
    debug: bool
    path: bool
    reveal: bool

    # run / sim options
    config_name: Optional[str] = Field(..., alias="<config>")
    working_dir: Optional[Path] = Field(..., alias="--working-dir")
    format: OutputFormat = Field("default", alias="--format")
    tags: Optional[str] = Field(..., alias="--tags")
    skip_tags: Optional[str] = Field(..., alias="--skip-tags")

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
    arguments = docopt(
        __doc__,
        version=f"organize v{__version__}",
        default_help=True,
    )
    args = CliArgs.model_validate(arguments)
    _execute = partial(
        execute,
        config=args.config_name,
        working_dir=args.working_dir,
        format=args.format,
        tags=args.tags,
        skip_tags=args.skip_tags,
    )
    try:
        if args.run:
            _execute(simulate=False)
        elif args.sim:
            _execute(simulate=True)
        elif args.config:
            if args.init:
                config_init(config=args.config_name)
            elif args.edit:
                config_edit(config=args.config_name)
            elif args.check:
                config_check(config=args.config_name)
            elif args.debug:
                config_debug(config=args.config_name)
            elif args.path:
                config_path(config=args.config_name)
            elif args.reveal:
                config_reveal(config=args.config_name)
        elif args.docs:
            docs()
    except (ConfigError, ConfigNotFound) as e:
        from rich import print

        print(e)
        sys.exit(1)


if __name__ == "__main__":
    cli()
