import logging
from enum import Enum
from typing import List, Union

import fs
from fs.errors import ResourceNotFound
from fs.base import FS
from pydantic import BaseModel, Field, validator
from . import console
from .actions import ActionType
from .filters import FilterType
from .location import Location
from .utils import fs_path_expand

logger = logging.getLogger(__name__)

rule_count = 0


def rule_name():
    global rule_count
    rule_count += 1
    return "Unnamed rule %s" % rule_count


def normalize_filter_or_action_definition(value):
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


class FilterMode(str, Enum):
    all = "all"
    any = "any"
    none = "none"


class RuleTarget(str, Enum):
    dirs = "dirs"
    files = "files"


class Rule(BaseModel):
    name: Union[str, None] = Field(default_factory=rule_name)
    enabled: bool = Field(True)
    targets: RuleTarget = RuleTarget.files
    locations: List[Location]
    subfolders: bool = False
    tags: List[str] = Field(default_factory=list)
    filters: List[FilterType] = Field(default_factory=list)
    filter_mode: FilterMode = FilterMode.all
    actions: List[ActionType] = Field(..., min_items=1)

    class Config:
        title = "A rule definition"
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
        return normalize_filter_or_action_definition(value)

    @validator("filters", pre=True, each_item=True)
    def validate_filters(cls, value):
        normalized = normalize_filter_or_action_definition(value)
        # handle inverting filters by prepending `not`
        if isinstance(normalized, dict):
            if normalized["name"].startswith("not "):
                _, name = normalized["name"].split()
                normalized["name"] = name
                normalized["filter_is_inverted"] = True
                return normalized
        return normalized

    def walk(self, working_dir: Union[FS, str] = "."):
        """
        Walk all given locations and yield the pathes
        """
        for location in self.locations:
            # instantiate the fs walker
            exclude = location.system_exclude_files + location.exclude_files
            exclude_dirs = location.system_exclude_dirs + location.exclude_dirs
            if location.max_depth == "inherit":
                max_depth = None if self.subfolders else 0
            else:
                max_depth = location.max_depth
            walker = fs.walk.Walker(
                ignore_errors=location.ignore_errors,
                on_error=None,
                search=location.search,
                exclude=exclude,
                exclude_dirs=exclude_dirs,
                max_depth=max_depth,
                filter=location.filter,
                filter_dirs=location.filter_dirs,
            )

            # whether to walk dirs or files
            _walk_funcs = {
                RuleTarget.files: walker.files,
                RuleTarget.dirs: walker.dirs,
            }
            walk_func = _walk_funcs[self.targets]

            _filesystem, _path = fs_path_expand(
                path=location.path,
                filesystem=location.filesystem,
                working_dir=working_dir,
            )

            fs_base_path = fs.path.forcedir(fs.path.relpath(fs.path.normpath(_path)))
            filesystem = fs.open_fs(_filesystem)
            console.location(filesystem, _path)
            for resource in walk_func(fs=filesystem, path=_path):
                # fs_path: no starting "./", no ending "/"
                # fs_base_path: no starting "./", ends with "/"
                fs_path = fs.path.relpath(resource)

                # skip broken symlinks
                try:
                    if filesystem.islink(fs_path):
                        continue
                except ResourceNotFound:
                    continue

                yield {
                    "fs": filesystem,
                    "fs_path": fs_path,
                    "fs_base_path": fs_base_path,
                    "working_dir": working_dir,
                }


if __name__ == "__main__":
    from organize.core import run

    with fs.open_fs("mem://") as mem:
        mem.touch("test")
        mem.touch("test2")
        conf = """
        rules:
          - locations:
              - path: "~/Desktop"
            actions:
              - echo: "test"
        """
        run(config=conf, working_dir="~")
