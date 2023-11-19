from pathlib import Path
from typing import Iterable, Optional

from pydantic import ValidationError


class ConfigError(ValueError):
    def __init__(self, e: ValidationError, config_path: Optional[Path] = None):
        self.e = e
        self.config_path = config_path.resolve() if config_path else None

    def __str__(self):
        count = self.e.error_count()
        title = self.config_path or self.e.title

        lines = [
            f'{count} validation error{"s" if count != 1 else ""} in "{title}"',
            "",
        ]
        for err in self.e.errors(include_url=False):
            loc = ".".join(str(x) for x in err["loc"])
            msg = err["msg"]
            inp_name = err["input"]
            inp_type = type(err["input"]).__name__
            inp = f'[input_value="{inp_name}", input_type={inp_type}]'
            lines.append(loc)
            lines.append(f"  {msg} {inp}")
        return "\n".join(lines)

    def json(self):
        return self.e.json()


class ConfigNotFound(FileNotFoundError):
    def __init__(
        self,
        config: str,
        search_pathes: Iterable[Path] = tuple(),
        init_path: Optional[Path] = None,
    ):
        self.config = config
        self.search_pathes = search_pathes
        self.init_path = init_path

    def __str__(self):
        msg = f'Cannot find config "{self.config}".'
        if self.search_pathes:
            path_listing = "\n".join(f' - "{path}"' for path in self.search_pathes)
            return f"{msg}\nSearch locations:\n{path_listing}"
        return msg
