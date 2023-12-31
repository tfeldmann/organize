from pathlib import Path
from typing import ClassVar, Set, Tuple

from pydantic import Field, field_validator
from pydantic.config import ConfigDict
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


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Extension:
    """Filter by file extension

    Attributes:
        *extensions (list(str) or str):
            The file extensions to match (does not need to start with a colon).

    **Returns:**

    - `{extension}`: the original file extension (without colon)
    """

    extensions: Set[str] = Field(default_factory=set)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="extension",
        files=True,
        dirs=False,
    )

    @field_validator("extensions", mode="before")
    def normalize_extensions(cls, v):
        as_list = convert_to_list(v)
        return set(map(normalize_extension, flatten(list(as_list))))

    def suffix_match(self, path: Path) -> Tuple[str, bool]:
        suffix = path.suffix.lstrip(".")
        if not self.extensions:
            return (suffix, True)
        if not suffix:
            return (suffix, False)
        return (suffix, normalize_extension(suffix) in self.extensions)

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        if res.is_dir():
            raise ValueError("Dirs not supported")

        suffix, match = self.suffix_match(path=res.path)
        res.vars[self.filter_config.name] = suffix
        return match
