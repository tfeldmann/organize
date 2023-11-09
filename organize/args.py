__doc__ = """
organize - The file management automation tool.

Usage:
  organize run [options] [<config>]
  organize sim [options] [<config>]
  organize edit [<config>]
  organize check [--verbose]
  organize reveal [--path]
  organize docs
  organize --version
  organize (-h | --help)

Commands:
  run       Organize your files.
  sim       Simulate organizing your files.
  edit      Edit the config file.
  check     Check config file validity.
  reveal    Reveal the config file.
  docs      Open the documentation.

Options:
  <config>                        A config name or path to a config file
  -w --working-dir <dir>          The working directory
  -f --format (default|JSONL)     The output format [Default: default]
  --tags <tags>                   tags to run (eg. "initial,release")
  --skip-tags <tags>              tags to skip
"""
from functools import partial
from pathlib import Path
from typing import Literal, Optional

from __version__ import __version__
from docopt import docopt
from pydantic import BaseModel, Field
from rich import print

from organize import Config
from organize.find_config import ConfigNotFound, find_config
from organize.output import JSONL, Default

DOCS_RTD = "https://organize.readthedocs.io"
DOCS_GHPAGES = "https://tfeldmann.github.io/organize/"


class CliArgs(BaseModel):
    run: bool
    sim: bool
    edit: bool
    check: bool
    reveal: bool
    docs: bool

    config: Optional[str] = Field(..., alias="<config>")
    working_dir: Optional[Path] = Field(..., alias="--working-dir")
    format: Literal["default", "jsonl"] = Field("default", alias="--format")
    tags: Optional[str] = Field("", alias="--tags")
    skip_tags: Optional[str] = Field("", alias="--skip-tags")
    verbose: bool = Field(..., alias="--verbose")
    path: bool = Field(..., alias="--path")


def execute(
    config: str,
    working_dir: Optional[Path],
    format: Literal["default", "jsonl"],
    tags: str,
    skip_tags: str,
    simulate: bool,
):
    output = JSONL() if format == "jsonl" else Default()
    try:
        config_path = find_config(config)
    except ConfigNotFound as e:
        print(e)
        return
    Config.from_path(config_path).execute(simulate=simulate, output=output)


def edit(config: str):
    pass


def check(verbose: bool):
    pass


def reveal(path: bool):
    pass


def docs():
    pass


def cli():
    arguments = docopt(
        __doc__,
        version=f"organize v{__version__}",
        default_help=True,
    )
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
    elif args.edit:
        edit(config=args.config)
    elif args.check:
        check(verbose=args.verbose)
    elif args.reveal:
        reveal(path=args.path)
    elif args.docs:
        docs()


if __name__ == "__main__":
    cli()
