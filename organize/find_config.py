import os
from itertools import chain
from pathlib import Path
from typing import Iterator, Optional, Tuple

import platformdirs

from organize.utils import expandvars

from .errors import ConfigNotFound

ENV_ORGANIZE_CONFIG = os.environ.get("ORGANIZE_CONFIG")
USER_CONFIG_DIR = platformdirs.user_config_path(appname="organize")
XDG_CONFIG_DIR = expandvars(os.environ.get("XDG_CONFIG_HOME", "~/.config")) / "organize"


def find_config(name_or_path: Optional[str] = None) -> Path:
    if name_or_path is None:
        if ENV_ORGANIZE_CONFIG is not None:
            # if the `ORGANIZE_CONFIG` env variable is defined we only check this
            # specific location
            result = expandvars(ENV_ORGANIZE_CONFIG)
            if result.exists() and result.is_file():
                return result
            else:
                raise ConfigNotFound(str(result), init_path=result)
        # no name and no ORGANIZE_CONFIG env variable given:
        # -> check only the default config
        result = USER_CONFIG_DIR / "config.yaml"
        if result.exists() and result.is_file():
            return result
        else:
            raise ConfigNotFound(str(result), init_path=result)

    # otherwise we try:
    # 0. The full path if applicable
    # 1.`$PWD`
    # 2. the platform specifig config dir
    # 3. `$XDG_CONFIG_HOME/organize`
    as_path = expandvars(name_or_path)
    if as_path.exists() and as_path.is_file():
        return as_path

    search_pathes: Tuple[Path, ...] = tuple()
    if not as_path.is_absolute():
        as_yml = Path(f"{as_path}.yml")
        as_yaml = Path(f"{as_path}.yaml")
        search_pathes = (
            as_path,
            as_yaml,
            as_yml,
            USER_CONFIG_DIR / as_path,
            USER_CONFIG_DIR / as_yaml,
            USER_CONFIG_DIR / as_yml,
            XDG_CONFIG_DIR / as_path,
            XDG_CONFIG_DIR / as_yaml,
            XDG_CONFIG_DIR / as_yml,
        )
        for path in search_pathes:
            if path.exists() and path.is_file():
                return path
    raise ConfigNotFound(
        config=name_or_path,
        search_pathes=search_pathes,
        init_path=USER_CONFIG_DIR / as_yaml,
    )


def list_configs() -> Iterator[Path]:
    for loc in (USER_CONFIG_DIR, XDG_CONFIG_DIR):
        yield from chain(loc.glob("*.yml"), loc.glob("*.yaml"))
