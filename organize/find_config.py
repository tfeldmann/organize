import os
from itertools import chain, product
from pathlib import Path
from typing import Iterator, Optional

import platformdirs

from organize.utils import expandvars

from .errors import ConfigNotFound

DOCS_RTD = "https://organize.readthedocs.io"
DOCS_GHPAGES = "https://tfeldmann.github.io/organize/"

ENV_ORGANIZE_CONFIG = os.environ.get("ORGANIZE_CONFIG")
XDG_CONFIG_DIR = expandvars(os.environ.get("XDG_CONFIG_HOME", "~/.config")) / "organize"
USER_CONFIG_DIR = platformdirs.user_config_path(appname="organize")

SEARCH_DIRS = (
    XDG_CONFIG_DIR,
    USER_CONFIG_DIR,
)


def find_config_by_name(name: str) -> Path:
    stem = Path(name).stem
    filenames = (
        f"{stem}.yaml",
        f"{stem}.yml",
        name,
    )
    search_dirs = (
        Path("."),
        *SEARCH_DIRS,
    )

    search_pathes = [d / f for d, f in product(search_dirs, filenames)]
    for path in search_pathes:
        if path.is_file():
            return path

    raise ConfigNotFound(config=stem, search_pathes=search_pathes)


def find_default_config() -> Path:
    # if the `ORGANIZE_CONFIG` env variable is set we only check this specific location
    if ENV_ORGANIZE_CONFIG is not None:
        result = expandvars(ENV_ORGANIZE_CONFIG)
        if result.exists() and result.is_file():
            return result
        raise ConfigNotFound(str(result))

    # otherwise we check all default locations for "config.y[a]ml"
    return find_config_by_name("config")


def find_config(name_or_path: Optional[str] = None) -> Path:
    # No config given? Find the default one.
    if name_or_path is None:
        return find_default_config()

    # Maybe we are given the path to a config file?
    as_path = expandvars(name_or_path)
    if as_path.is_file():
        return as_path

    # search the default locations for the given name
    return find_config_by_name(name=name_or_path)


def list_configs() -> Iterator[Path]:
    for loc in SEARCH_DIRS:
        yield from chain(loc.glob("*.yml"), loc.glob("*.yaml"))


EXAMPLE_CONFIG = f"""\
# organize configuration file
# {DOCS_RTD}

rules:
  - locations:
    filters:
    actions:
      - echo: "Hello, World!"
"""


def example_config_path(name_or_path: Optional[str]) -> Path:
    # prefer "~/.config/organize" if it is already present on the system
    preferred_dir = XDG_CONFIG_DIR if XDG_CONFIG_DIR.is_dir() else USER_CONFIG_DIR

    if name_or_path is None:
        if ENV_ORGANIZE_CONFIG is not None:
            return expandvars(ENV_ORGANIZE_CONFIG)
        return preferred_dir / "config.yaml"

    # maybe we are given a path to create the config there?
    if "/" in name_or_path or "\\" in name_or_path:
        return expandvars(name_or_path)

    # create at preferred dir -
    # - keeping the extension
    if name_or_path.lower().endswith((".yml", ".yaml")):
        return preferred_dir / name_or_path
    # - with .yaml extension
    return preferred_dir / f"{name_or_path}.yaml"


def create_example_config(name_or_path: Optional[str] = None) -> Path:
    path = example_config_path(name_or_path=name_or_path)
    if path.is_file():
        raise FileExistsError(f'Config "{path.absolute()}" already exists.')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(EXAMPLE_CONFIG, encoding="utf-8")
    return path
