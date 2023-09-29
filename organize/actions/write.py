from enum import Enum
from pathlib import Path
from typing import ClassVar

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.utils import Template


class Mode(str, Enum):
    prepend = "prepend"
    append = "append"
    overwrite = "overwrite"


@dataclass
class Write:

    """
    Write text to a file.

    If the specified path does not exist it will be created.

    Args:
        text (str):
            The text that should be written. Supports templates.

        file (str):
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
            This happens only the first time write_file is run. If the rule filters
            don't match anything the file is left as it is.
            Defaults to `false`.

        filesystem (str):
            (Optional) A pyfilesystem opener url of the filesystem the textfile is on.
            If this is not given, the local filesystem is used.
    """

    text: str
    path: str
    mode: Mode = Mode.append
    newline: bool = True
    clear_before_first_write: bool = False

    action_config: ClassVar = ActionConfig(
        name="write",
        standalone=True,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._text = Template.from_string(self.text)
        self._path = Template.from_string(self.path)
        self._is_first_write = True

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        text = self._text.render(**res.dict())
        path = Path(self._path.render(**res.dict()))

        if self._is_first_write:
            # reset flag
            self._is_first_write = False

            # create parent folders
            path.parent.mkdir(parents=True, exist_ok=True)

            # optionally clear if path exists
            if path.exists() and self.clear_before_first_write:
                output.msg(res=res, msg=f"Clearing file {path}", sender=self)
                if not simulate:
                    with path.open("w"):
                        pass

        output.msg(res=res, msg=f'{path}: {self.mode} "{text}"', sender=self)
        if self.newline:
            text += "\n"

        if not simulate:
            if self.mode == Mode.append:
                with open(path, "a") as f:
                    f.write(text)
            elif self.mode == Mode.prepend:
                content = ""
                if path.exists():
                    content = path.read_text()
                path.write_text(text + content)
            elif self.mode == Mode.overwrite:
                path.write_text(text)
