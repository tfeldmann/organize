import logging
import sys
from typing import List, Union

import simplematch as sm
from pydantic import Field
from typing_extensions import Literal

from organize.utils import Template
from organize.validators import ensure_list

from .action import Action

logger = logging.getLogger(__name__)


class MacOSTags(Action):

    """Add macOS tags.

    Args:
        *tags (str): A list of tags or a single tag.

    The color can be specified in brackets after the tag name, for example:

    ```yaml
    macos_tags: "Invoices (red)"
    ```

    Available colors are `none`, `gray`, `green`, `purple`, `blue`, `yellow`, `red` and
    `orange`.
    """

    name: Literal["macos_tags"] = Field("macos_tags", repr=False)
    tags: Union[List[str], str]

    _tags: list
    _validate_tags = ensure_list("tags")

    class ParseConfig:
        accepts_positional_arg = "tags"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tags = [Template.from_string(tag) for tag in self.tags]

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]
        fs_path = args["fs_path"]
        path = fs.getsyspath(fs_path)

        if sys.platform != "darwin":
            raise EnvironmentError("The macos_tags action is only available on macOS")

        import macos_tags

        COLORS = [c.name.lower() for c in macos_tags.Color]

        for template in self.tags:
            tag = template.render(**args)
            name, color = self._parse_tag(tag)

            if color not in COLORS:
                raise ValueError(
                    "color %s is unknown. (Available: %s)" % (color, " / ".join(COLORS))
                )

            self.print('Adding tag: "%s" (color: %s)' % (name, color))
            if not simulate:
                _tag = macos_tags.Tag(
                    name=name,
                    color=macos_tags.Color[color.upper()],
                )  # type: ignore
                macos_tags.add(_tag, file=str(path))

    def _parse_tag(self, s):
        """parse a tag definition and return a tuple (name, color)"""
        result = sm.match("{name} ({color})", s)
        if not result:
            return s, "none"
        return result["name"], result["color"].lower()
