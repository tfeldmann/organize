import sys
from typing import List, Union

import simplematch as sm
from pydantic import Field
from typing_extensions import Literal

from organize.validators import ensure_list

from .filter import Filter, FilterResult


def list_tags(path):
    import macos_tags

    tags = macos_tags.get_all(path)
    return ["{} ({})".format(tag.name, tag.color.name.lower()) for tag in tags]


class MacOSTags(Filter):
    """Filter by macOS tags

    Args:
        *tags (list(str) or str):
            The tags to filter by
    """

    name: Literal["macos_tags"] = Field("macos_tags", repr=False)
    tags: Union[List[str], str]

    _tags: list
    _validate_tags = ensure_list("tags")

    class ParseConfig:
        accepts_positional_arg = "tags"

    def matches(self, tags: List[str]) -> Union[bool, str]:
        if not self.filter_tags:
            return True
        if not tags:
            return False
        for tag in tags:
            if any(sm.test(filter_tag, tag) for filter_tag in self.filter_tags):
                return True
        return False

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]
        fs_path = args["fs_path"]
        path = fs.getsyspath(fs_path)

        if sys.platform != "darwin":
            raise EnvironmentError("The macos_tags filter is only available on macOS")

        tags = list_tags(path)

        return FilterResult(
            matches=bool(self.matches(tags)),
            updates={self.name: tags},
        )
