import os
from pathlib import Path
from typing import Optional, Tuple

import platformdirs

from organize.utils import expandvars


class ConfigNotFound(FileNotFoundError):
    def __init__(self, config: str, search_pathes: Tuple[str]):
        self.config = config
        self.search_pathes = search_pathes

    def __str__(self):
        msg = f'Cannot find config "{self.config}".'
        if self.search_pathes:
            path_listing = "\n".join(f' - "{path}"' for path in self.search_pathes)
            return f"{msg}\nSearch locations:\n{path_listing}"
        return msg


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

    search_pathes = tuple()
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
            XDG_CONFIG_HOME / as_path,
            XDG_CONFIG_HOME / as_yaml,
            XDG_CONFIG_HOME / as_yml,
        )
        for path in search_pathes:
            if path.exists():
                return path
    raise ConfigNotFound(config=name_or_path, search_pathes=search_pathes)
