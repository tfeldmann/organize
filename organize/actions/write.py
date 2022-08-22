from typing_extensions import Literal
import logging
from enum import Enum
from typing import Union

from fs.base import FS
from fs.opener import manage_fs

from organize.utils import Template

from ._utils import open_create_fs_path
from .action import Action

logger = logging.getLogger(__name__)


class Mode(str, Enum):
    prepend = "prepend"
    append = "append"
    overwrite = "overwrite"


class Write(Action):

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

    name: Literal["write"] = "write"
    text: str
    path: str
    mode: Mode = Mode.append
    newline: bool = True
    clear_before_first_write: bool = False
    filesystem: Union[FS, str, None] = None

    _text: Template
    _path: Template
    _is_first_write: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = Template.from_string(self.text)
        self._path = Template.from_string(self.path)
        self._is_first_write = True
        # self.filesystem = filesystem or self.Meta.default_filesystem

    def pipeline(self, args: dict, simulate: bool):
        text = self._text.render(args)
        path = self._path.render(args)

        dst_fs, dst_path = open_create_fs_path(
            fs=self.filesystem,
            path=path,
            args=args,
            simulate=simulate,
        )

        if self._is_first_write and self.clear_before_first_write:
            self.print(f"Clearing file {dst_path}")
            if not simulate:
                dst_fs.create(dst_path, wipe=True)

        self.print(f'{path}: {self.mode} "{text}"')
        if self.newline:
            text += "\n"

        if not simulate:
            with manage_fs(dst_fs):
                if self.mode == Mode.append:
                    dst_fs.appendtext(dst_path, text)
                elif self.mode == Mode.prepend:
                    content = ""
                    if dst_fs.exists(dst_path):
                        content = dst_fs.readtext(dst_path)
                    dst_fs.writetext(dst_path, text + content)
                elif self.mode == Mode.overwrite:
                    dst_fs.writetext(dst_path, text)

        self._is_first_write = False
