from pathlib import Path
from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize import duplicates
from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render


@dataclass(config=ConfigDict(extra="forbid"))
class MarkDuplicate:
    """Marks a file as a duplicate so you can review it later.

    On macOS the file gets the Finder tag "Duplicate", so all duplicates can be found
    in the Finder sidebar. The path of the original is stored with the file and kept
    when the file is moved (`organize duplicates` lists all marked files).

    Attributes:
        original (str):
            The original file. Defaults to `{copy_of.original}`, as found by the
            [copy_of](filters.md#copy_of) filter.
        tag (str): The Finder tag. Defaults to `Duplicate`.
        color (str): The color of the tag. Defaults to `red`.
    """

    original: str = "{copy_of.original}"
    tag: str = duplicates.TAG
    color: str = "red"

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="mark_duplicate",
        standalone=False,
        files=True,
        dirs=False,
    )

    def __post_init__(self):
        self._original = Template.from_string(self.original)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        assert res.path is not None, "Does not support standalone mode"
        original = Path(render(self._original, res.dict()))
        output.msg(res=res, msg=f"Duplicate of {original}", sender=self)
        if not simulate:
            duplicates.mark(res.path, original, tag=self.tag, color=self.color)
