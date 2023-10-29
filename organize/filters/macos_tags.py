import sys
from typing import ClassVar, List

from pydantic import Field, field_validator
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.utils import glob_match


def list_tags(path) -> List[str]:
    import macos_tags

    tags = macos_tags.get_all(path)
    return ["{} ({})".format(tag.name, tag.color.name.lower()) for tag in tags]


def matches_tags(filter_tags, file_tags) -> bool:
    if not filter_tags:
        return True
    if not file_tags:
        return False
    for tag in file_tags:
        if any(glob_match(filter_tag, tag) for filter_tag in filter_tags):
            return True
    return False


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class MacOSTags:
    """Filter by macOS tags

    Args:
        tags (list(str) or str):
            The tags to filter by
    """

    tags: List[str] = Field(default_factory=list)

    filter_config: ClassVar = FilterConfig(name="macos_tags", files=True, dirs=True)

    def __post_init__(self):
        if sys.platform != "darwin":
            raise EnvironmentError("The macos_tags filter is only available on macOS")

    @field_validator("tags", mode="before")
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    def pipeline(self, res: Resource, output: Output) -> bool:
        file_tags = list_tags(res.path)
        res.vars[self.filter_config.name] = file_tags
        return matches_tags(filter_tags=self.tags, file_tags=file_tags)
