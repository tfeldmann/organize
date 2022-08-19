from enum import Enum
from typing import List, Union

import fs
from fs.base import FS
from fs.walk import Walker
from pydantic import BaseModel, Field, validator
from typing_extensions import Annotated

from .location import Location
from .pydantic_actions import Action, Copy, Move
from .pydantic_filters import Empty, Filter, Name
from .utils import fs_path_expand


def normalize_config_object(value):
    """
    Transform input like {"extension": {**args}} to {"name": "extension", **args}
    """
    if isinstance(value, str):
        return {"name": value}
    if isinstance(value, dict):
        if len(value.keys()) != 1:
            keys = ", ".join(value.keys())
            raise ValueError("Definition must have a single key (found: %s)" % keys)
        name = list(value.keys())[0]
        args = value[name]
        # if anything but a dictionary is given we assign it to the special key
        # __positional_arg__, which is then handled in the root validator of the
        # instantiated class.
        if not isinstance(args, dict):
            return {"name": name, "__positional_arg__": args}
        return {"name": name, **args}
    # anything else we just return. Could be an instance of an allowed class.
    return value


ActionType = Union[
    Action,
    Annotated[
        Union[Move, Copy],
        Field(discriminator="name"),
    ],
]
FilterType = Union[
    Filter,
    Annotated[
        Union[Name, Empty],
        Field(discriminator="name"),
    ],
]


class FilterMode(str, Enum):
    all = "all"
    any = "any"
    none = "none"


class RuleTarget(str, Enum):
    dirs = "dirs"
    files = "files"


class Rule(BaseModel):
    name: Union[str, None] = None
    enabled: bool = Field(True, repr=False)
    targets: RuleTarget = RuleTarget.files
    locations: List[Location]
    subfolders: bool = False
    filesystem: Union[FS, str, None] = None
    filters: List[FilterType] = Field(default_factory=list)
    filter_mode: FilterMode = FilterMode.all
    actions: List[ActionType] = Field(..., min_items=1)

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True

    @validator("locations", pre=True)
    def validate_locations(cls, v):
        if v is None:
            raise ValueError("Location cannot be empty")
        if isinstance(v, str):
            v = {"path": v}
        if not isinstance(v, list):
            v = [v]
        return v

    @validator("actions", pre=True, each_item=True)
    def action_rewriter(cls, value):
        return normalize_config_object(value)

    @validator("filters", pre=True, each_item=True)
    def validate_filters(cls, value):
        normalized = normalize_config_object(value)
        # handle inverting filters by prepending `not`
        if isinstance(normalized, dict):
            if normalized["name"].startswith("not "):
                _, name = normalized["name"].split()
                normalized["name"] = name
                normalized["filter_is_inverted"] = True
                return normalized
        return normalized

    def walk(self):
        """
        Walk all given locations and yield the pathes
        """
        for location in self.locations:
            exclude = location.system_exclude_files + location.exclude_files
            exclude_dirs = location.system_exclude_dirs + location.exclude_dirs
            if location.max_depth == "inherit":
                max_depth = None if self.subfolders else 0
            else:
                max_depth = location.max_depth
            walker = Walker(
                ignore_errors=location.ignore_errors,
                on_error=None,
                search=location.search,
                exclude=exclude,
                exclude_dirs=exclude_dirs,
                max_depth=max_depth,
                filter=location.filter,
                filter_dirs=location.filter_dirs,
            )
            _walk_funcs = {
                RuleTarget.files: walker.files,
                RuleTarget.dirs: walker.dirs,
            }
            walk_func = _walk_funcs[self.targets]
            if location.filesystem == "inherit":
                _filesystem = self.filesystem
            else:
                _filesystem = location.filesystem

            _filesystem, _path = fs_path_expand(path=location.path, fs=_filesystem)
            with fs.open_fs(_filesystem) as filesystem:
                for result in walk_func(fs=filesystem, path=_path):
                    fs_path = fs.path.relpath(result)
                    fs_base_path = fs.path.relpath(fs.path.normpath(_path))
                    yield {
                        "fs": filesystem,
                        "fs_path": fs_path,
                        "fs_base_path": fs_base_path,
                    }


if __name__ == "__main__":
    rule = Rule(
        name="Test",
        locations={
            "exclude_dirs": [".venv", ".mypy_cache"],
            "path": "/Desktop/usbhub/",
            "filesystem": "~",
        },
        subfolders=True,
        targets="files",
        actions=[Move(dest="tst")],
    )
    for result in rule.walk():
        print(result)
