from enum import Enum
from typing import List, Union

from fs.base import FS
from pydantic import BaseModel, Field, validator
from typing_extensions import Literal

DEFAULT_SYSTEM_EXCLUDE_FILES = [
    "thumbs.db",
    "desktop.ini",
    "~$*",
    ".DS_Store",
    ".localized",
]

DEFAULT_SYSTEM_EXCLUDE_DIRS = [
    ".git",
    ".svn",
]


class SearchMethod(str, Enum):
    depth = "depth"
    breadth = "breadth"


class Location(BaseModel):
    path: str
    max_depth: Union[Literal["rule_setting"], int, None] = "rule_setting"
    search: SearchMethod = SearchMethod.depth
    exclude_files: List[str] = Field(default_factory=list)
    exclude_dirs: List[str] = Field(default_factory=list)
    system_exclude_files: List[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_FILES
    )
    system_exclude_dirs: List[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_DIRS
    )
    filter: List[str] = Field(default_factory=list)
    filter_dirs: List[str] = Field(default_factory=list)
    ignore_errors: bool = False
    filesystem: Union[str, FS] = ""

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True

    @validator(
        "exclude_files",
        "exclude_dirs",
        "system_exclude_files",
        "system_exclude_dirs",
        pre=True,
    )
    def ensure_list(cls, value):
        if isinstance(value, str):
            return [value]
        return value


if __name__ == "__main__":
    print(Location(path="."))
