__doc__ = """
organize - The file management automation tool.

Usage:
  organize run    [options] [<config> | --stdin]
  organize sim    [options] [<config> | --stdin]
  organize watch  [options] [--delay <seconds>] [<config>]
  organize undo   [--dry-run] [--run <id>]
  organize history
  organize info   [<config>]
  organize move   <src> <dest>
  organize new    [<config>]
  organize edit   [<config>]
  organize check  [<config> | --stdin]
  organize debug  [<config> | --stdin]
  organize show   [--path|--reveal] [<config>]
  organize list
  organize docs
  organize --version
  organize --help

Commands:
  run        Organize your files.
  sim        Simulate organizing your files.
  watch      Organize your files whenever files are added to a location.
               Waits until no new files arrived for --delay seconds.
  undo       Undo the last run (or the run given by --run).
               Use --dry-run to only show what would be undone.
  history    List the runs that can be undone.
  info       Print the folders and AI categories of a config as JSON.
  move       Move <src> into the folder <dest> as an undoable run.
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
  <config>                        A config name or path to a config file.
                                  Some commands also support piping in a config file
                                  via the `--stdin` flag.
  -W --working-dir <dir>          The working directory
  -F --format (default|errorsonly|JSONL)
                                  The output format [Default: default]
  -T --tags <tags>                Tags to run (eg. "initial,release")
  -S --skip-tags <tags>           Tags to skip
  --delay <seconds>               Seconds to wait after a change [Default: 5]
  --run <id>                      A run id as shown by `organize history`
  --dry-run                       Only show what would be done
  -h --help                       Show this help page.
"""
import os
import sys
from functools import partial
from pathlib import Path
from typing import Annotated, Literal, Optional, Set, Union

from docopt import docopt
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)
from pydantic.functional_validators import BeforeValidator
from rich.console import Console
from rich.pretty import pprint
from rich.syntax import Syntax
from rich.table import Table
from yaml.scanner import ScannerError

from organize import Config, ConfigError, history
from organize.find_config import (
    DOCS_RTD,
    ConfigNotFound,
    create_example_config,
    find_config,
    list_configs,
)
from organize.logger import enable_logfile
from organize.output import JSONL, Default, Output
from organize.utils import escape

from .__version__ import __version__

Tags = Set[str]
OutputFormat = Annotated[
    Literal["default", "jsonl", "errorsonly"], BeforeValidator(lambda v: v.lower())
]

console = Console()


class ConfigWithPath(BaseModel):
    """
    Allows reading the config from a path, finding it by name or supplying it directly
    via stdin.
    """

    config: str
    config_path: Optional[Path]

    @classmethod
    def from_stdin(cls) -> "ConfigWithPath":
        return cls(config=sys.stdin.read(), config_path=None)

    @classmethod
    def by_name_or_path(cls, name_or_path: Optional[str]) -> "ConfigWithPath":
        config_path = find_config(name_or_path=name_or_path)
        return cls(
            config=config_path.read_text(encoding="utf-8"),
            config_path=config_path,
        )

    def path(self):
        if self.config_path is not None:
            return str(self.config_path)
        return "[config given by string / stdin]"


def _open_uri(uri: str) -> None:
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
    config: ConfigWithPath,
    working_dir: Optional[Path],
    format: OutputFormat,
    tags: Tags,
    skip_tags: Tags,
    simulate: bool,
) -> None:
    Config.from_string(
        config=config.config,
        config_path=config.config_path,
    ).execute(
        simulate=simulate,
        output=_output_for_format(format),
        tags=tags,
        skip_tags=skip_tags,
        working_dir=working_dir or Path("."),
    )


def watch(
    config: Optional[str],
    working_dir: Optional[Path],
    format: OutputFormat,
    tags: Tags,
    skip_tags: Tags,
    delay: float,
) -> None:
    from organize.watch import watch as watch_

    def load_config() -> Config:
        conf = ConfigWithPath.by_name_or_path(config)
        return Config.from_string(config=conf.config, config_path=conf.config_path)

    def run(conf: Config) -> None:
        conf.execute(
            simulate=False,
            output=_output_for_format(format),
            tags=tags,
            skip_tags=skip_tags,
            working_dir=working_dir or Path("."),
        )

    try:
        watch_(load_config=load_config, run=run, delay=delay)
    except KeyboardInterrupt:
        console.print("Stopped watching.")
    except ValueError as e:
        console.print(f"[red]Error:[/] {escape(e)}")
        sys.exit(1)


def undo(run_id: Optional[str], dry_run: bool) -> None:
    run = history.find_run(run_id) if run_id else history.last_run()
    if run is None:
        console.print("Nothing to undo.")
        sys.exit(1)
    if run.undone:
        console.print(f"Run {escape(run.id)} was already undone.")
        sys.exit(1)
    verb = "Would undo" if dry_run else "Undoing"
    console.print(f"{verb} run {escape(run.id)} from {escape(run.time)}:")
    for msg in history.undo(run, simulate=dry_run):
        console.print(f"  {escape(msg)}")


def info(config: Optional[str]) -> None:
    import json

    from organize import app_support

    conf = ConfigWithPath.by_name_or_path(config)
    parsed = Config.from_string(config=conf.config, config_path=conf.config_path)
    print(json.dumps({**app_support.info(parsed), "config_path": conf.path()}))


def move(src: str, dest: str) -> None:
    import json

    from organize import app_support

    try:
        dst = app_support.move(Path(src), Path(dest))
    except OSError as e:
        console.print(f"[red]Error:[/] {escape(e)}")
        sys.exit(1)
    print(json.dumps({"dst": str(dst)}))


def history_() -> None:
    table = Table()
    table.add_column("Run", no_wrap=True)
    table.add_column("Time", no_wrap=True)
    table.add_column("Files", justify="right")
    table.add_column("Undone")
    for run in history.runs():
        files = sum(op["op"] != "mkdir" for op in run.ops)
        table.add_row(run.id, run.time, str(files), "yes" if run.undone else "")
    console.print(table)


def new(config: Optional[str]) -> None:
    try:
        new_path = create_example_config(name_or_path=config)
        console.print(
            f'Config "{escape(new_path.name)}" created at "{escape(new_path.absolute())}"'
        )
    except FileExistsError as e:
        console.print(
            f"{e}\n"
            r'Use "organize new \[name]" to create a config in the default location.'
        )
        sys.exit(1)


def edit(config: Optional[str]) -> None:
    config_path = find_config(config)
    editor = os.getenv("EDITOR")
    if editor:
        os.system(f'{editor} "{config_path}"')
    else:
        _open_uri(config_path.as_uri())


def check(config: ConfigWithPath) -> None:
    Config.from_string(config=config.config, config_path=config.config_path)
    console.print(f'No problems found in "{escape(config.path())}".')


def debug(config: ConfigWithPath) -> None:
    conf = Config.from_string(config=config.config, config_path=config.config_path)
    pprint(conf, expand_all=True, indent_guides=False)


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
    uri = DOCS_RTD
    print(f'Opening "{escape(uri)}"')
    _open_uri(uri=uri)


class CliArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # commands
    run: bool
    sim: bool
    watch: bool
    undo: bool
    history: bool
    info: bool
    move: bool
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
    stdin: bool = Field(..., alias="--stdin")

    # watch / undo options
    delay: float = Field(5.0, alias="--delay")
    run_id: Optional[str] = Field(None, alias="--run")
    dry_run: bool = Field(False, alias="--dry-run")

    # move arguments
    src: Optional[str] = Field(None, alias="<src>")
    dest: Optional[str] = Field(None, alias="<dest>")

    # show options
    path: bool = Field(False, alias="--path")
    reveal: bool = Field(False, alias="--reveal")

    # docopt options
    version: bool = Field(..., alias="--version")
    help: bool = Field(..., alias="--help")

    @model_validator(mode="after")
    def either_stdin_or_config(self):
        if self.stdin and self.config is not None:
            raise ValueError("Either set a config file or --stdin.")
        return self


def _split_tags(val: Optional[str]) -> Tags:
    if val is None:
        return set()
    return set(val.split(","))


def cli(argv: Union[list[str], str, None] = None) -> None:
    enable_logfile()
    assert __doc__ is not None
    parsed_args = docopt(
        __doc__,
        argv=argv,
        default_help=True,
        version=f"organize v{__version__}",
    )
    try:
        args = CliArgs.model_validate(parsed_args)

        def _config_with_path():
            if args.stdin:
                return ConfigWithPath.from_stdin()
            else:
                return ConfigWithPath.by_name_or_path(args.config)

        if args.sim or args.run:
            _execute = partial(
                execute,
                config=_config_with_path(),
                working_dir=args.working_dir,
                format=args.format,
                tags=_split_tags(args.tags),
                skip_tags=_split_tags(args.skip_tags),
            )
            if args.run:
                _execute(simulate=False)
            elif args.sim:
                _execute(simulate=True)
        elif args.watch:
            watch(
                config=args.config,
                working_dir=args.working_dir,
                format=args.format,
                tags=_split_tags(args.tags),
                skip_tags=_split_tags(args.skip_tags),
                delay=args.delay,
            )
        elif args.undo:
            undo(run_id=args.run_id, dry_run=args.dry_run)
        elif args.history:
            history_()
        elif args.info:
            info(config=args.config)
        elif args.move:
            assert args.src is not None and args.dest is not None
            move(src=args.src, dest=args.dest)
        elif args.new:
            new(config=args.config)
        elif args.edit:
            edit(config=args.config)
        elif args.check:
            check(config=_config_with_path())
        elif args.debug:
            debug(config=_config_with_path())
        elif args.show:
            show(config=args.config, path=args.path, reveal=args.reveal)
        elif args.list:
            list_()
        elif args.docs:
            docs()
    except (ConfigError, ConfigNotFound) as e:
        console.print(f"[red]Error: Config problem[/]\n{escape(e)}")
        sys.exit(1)
    except ValidationError as e:
        console.print(f"[red]Error: Invalid CLI arguments[/]\n{escape(e)}")
        sys.exit(2)
    except ScannerError as e:
        console.print(f"[red]Error: YAML syntax error[/]\n{escape(e)}")
        sys.exit(3)


if __name__ == "__main__":
    cli()
