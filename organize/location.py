from typing import List, Literal, Union

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .validators import FlatList, FlatSet

DEFAULT_SYSTEM_EXCLUDE_FILES = {
    "thumbs.db",
    "desktop.ini",
    "~$*",
    ".DS_Store",
    ".localized",
}

DEFAULT_SYSTEM_EXCLUDE_DIRS = {
    ".git",
    ".svn",
}


@dataclass(config=ConfigDict(extra="forbid"))
class Location:
    path: FlatList[str]
    min_depth: int = 0
    max_depth: Union[Literal["inherit"], int, None] = "inherit"
    search: Literal["depth", "breadth"] = "breadth"
    exclude_files: FlatSet[str] = Field(default_factory=set)
    exclude_dirs: FlatSet[str] = Field(default_factory=set)
    system_exclude_files: FlatSet[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_FILES
    )
    system_exclude_dirs: FlatSet[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_DIRS
    )
    filter: Union[List[str], None] = None
    filter_dirs: Union[List[str], None] = None
    ignore_errors: bool = False
