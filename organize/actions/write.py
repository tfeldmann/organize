from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.template import Template

if TYPE_CHECKING:
    from organize.output import Output
    from organize.resource import Resource


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Write:

    """
    Write text to a file.

    If the specified path does not exist it will be created.

    Args:
        text (str):
            The text that should be written. Supports templates.

        outfile (str):
            The file `text` should be written into. Supports templates.

        mode (str):
            Can be either `append` (append text to the file), `prepend` (insert text as
            first line) or `overwrite` (overwrite content with text).
            Defaults to `append`.

        newline (str):
            (Optional) Whether to append a newline to the given `text`.
            Defaults to `true`.

        clear_before_first_write (bool):
            (Optional) Clears the file before first appending / prepending text to it.
            This happens only the first time the file is written to. If the rule filters
            don't match anything the file is left as it is.
            Defaults to `false`.
    """

    text: str
    outfile: str
    mode: Literal["append", "prepend", "overwrite"] = "append"
    newline: bool = True
    clear_before_first_write: bool = False

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="write",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._text = Template.from_string(self.text)
        self._path = Template.from_string(self.outfile)
        self._known_files = set()

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        text = self._text.render(**res.dict())
        path = Path(self._path.render(**res.dict()))

        resolved = path.resolve()
        if resolved not in self._known_files:
            self._known_files.add(resolved)

            if not simulate:
                resolved.parent.mkdir(parents=True, exist_ok=True)

            # clear on first write
            if resolved.exists() and self.clear_before_first_write:
                output.msg(res=res, msg=f"Clearing file {path}", sender=self)
                if not simulate:
                    resolved.open("w")  # clear the file

        output.msg(res=res, msg=f'{path}: {self.mode} "{text}"', sender=self)
        if self.newline:
            text += "\n"

        if not simulate:
            if self.mode == "append":
                with open(path, "a") as f:
                    f.write(text)
            elif self.mode == "prepend":
                content = ""
                if path.exists():
                    content = path.read_text()
                path.write_text(text + content)
            elif self.mode == "overwrite":
                path.write_text(text)
