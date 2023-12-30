import sys
from typing import ClassVar

import simplematch as sm
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render
from organize.validators import FlatList


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class MacOSTags:

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

    tags: FlatList[str]

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="macos_tags",
        standalone=False,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        if sys.platform != "darwin":
            raise EnvironmentError("The macos_tags action is only available on macOS")

        self._tags = [Template.from_string(tag) for tag in self.tags]

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        import macos_tags

        COLORS = [c.name.lower() for c in macos_tags.Color]

        for template in self._tags:
            tag = render(template, res.dict())
            name, color = self._parse_tag(tag)

            if color not in COLORS:
                raise ValueError(
                    "color %s is unknown. (Available: %s)" % (color, " / ".join(COLORS))
                )

            output.msg(
                res=res,
                sender=self,
                msg=f'Adding tag: "{name}" (color: {color})',
            )
            if not simulate:
                _tag = macos_tags.Tag(
                    name=name,
                    color=macos_tags.Color[color.upper()],
                )  # type: ignore
                macos_tags.add(_tag, file=str(res.path))

    def _parse_tag(self, s):
        """parse a tag definition and return a tuple (name, color)"""
        result = sm.match("{name} ({color})", s)
        if not result:
            return s, "none"
        return result["name"], result["color"].lower()
