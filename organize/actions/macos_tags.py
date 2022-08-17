import logging
import sys

import simplematch as sm
from schema import Or

from organize.utils import Template

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

    name = "macos_tags"

    @classmethod
    def get_schema(cls):
        return {cls.name: Or(str, [str])}

    def __init__(self, *tags):
        self.tags = [Template.from_string(tag) for tag in tags]

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

    def __str__(self) -> str:
        return "MacOSTags(tags=%s)" % self.tags
