from typing import List, Literal, Set, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.dataclasses import dataclass

from .validators import FlatList

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
class Location(BaseModel):
    path: FlatList[str]
    min_depth: int = 0
    max_depth: Union[Literal["inherit"], int, None] = "inherit"
    search: Literal["depth", "breadth"] = "breadth"
    exclude_files: Set[str] = Field(default_factory=set)
    exclude_dirs: Set[str] = Field(default_factory=set)
    system_exclude_files: Set[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_FILES
    )
    system_exclude_dirs: Set[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_DIRS
    )
    filter: Union[List[str], None] = None
    filter_dirs: Union[List[str], None] = None
    ignore_errors: bool = False

    @field_validator(
        "exclude_files",
        "exclude_dirs",
        "system_exclude_files",
        "system_exclude_dirs",
        mode="before",
    )
    @classmethod
    def ensure_set(cls, value):
        if isinstance(value, str):
            return set([value])
        return set(value)
