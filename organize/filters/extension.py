from typing import ClassVar, Set

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.validators import flatten


def convert_to_list(v):
    if not v:
        return []
    if isinstance(v, str):
        return v.split()
    return v


def normalize_extension(ext: str) -> str:
    """strip colon and convert to lowercase"""
    if ext.startswith("."):
        return ext[1:].lower()
    else:
        return ext.lower()


@dataclass
class Extension:
    """Filter by file extension

    Args:
        *extensions (list(str) or str):
            The file extensions to match (does not need to start with a colon).

    **Returns:**

    - `{extension}`: the original file extension (without colon)
    """

    extensions: Set[str] = Field(default_factory=set)

    filter_config: ClassVar = FilterConfig(
        name="extension",
        files=True,
        dirs=False,
    )

    @field_validator("extensions", mode="before")
    def normalize_extensions(cls, v):
        as_list = convert_to_list(v)
        return list(map(normalize_extension, flatten(list(as_list))))

    def pipeline(self, res: Resource, output: Output) -> bool:
        if res.is_dir():
            raise ValueError("Dirs not supported")

        # suffix is the extension with dot
        suffix = res.path.suffix.lstrip(".")
        res.vars[self.filter_config.name] = suffix
        if not self.extensions:
            return True
        if not suffix:
            return False
        return normalize_extension(suffix) in self.extensions
