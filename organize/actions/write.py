import logging
from typing import Union

from fs.base import FS
from fs.opener import manage_fs
from schema import Optional, Or

from organize.utils import Template

from ._utils import open_create_fs_path
from .action import Action

logger = logging.getLogger(__name__)

MODES = (
    "prepend",
    "append",
    "overwrite",
)


class Write(Action):

    """Write text to a file.

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

    name = "write"
    arg_schema = Or(
        {
            "text": str,
            "path": str,
            Optional("mode"): Or(*MODES),
            Optional("newline"): bool,
            Optional("clear_before_first_write"): bool,
            Optional("filesystem"): object,
        },
    )

    def __init__(
        self,
        text: str,
        path: str,
        mode: str = "append",
        newline: bool = True,
        clear_before_first_write: bool = False,
        filesystem: Union[FS, str, None] = None,
    ) -> None:
        self.text = Template.from_string(text)
        self.path = Template.from_string(path)
        self.mode = mode.lower()
        self.clear_before_first_write = clear_before_first_write
        self.newline = newline
        self.filesystem = filesystem or self.Meta.default_filesystem

        self._is_first_write = True

        if self.mode not in MODES:
            raise ValueError("mode must be one of %s" % ", ".join(MODES))

    def pipeline(self, args: dict, simulate: bool):
        text = self.text.render(args)
        path = self.path.render(args)

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
                if self.mode == "append":
                    dst_fs.appendtext(dst_path, text)
                elif self.mode == "prepend":
                    content = ""
                    if dst_fs.exists(dst_path):
                        content = dst_fs.readtext(dst_path)
                    dst_fs.writetext(dst_path, text + content)
                elif self.mode == "overwrite":
                    dst_fs.writetext(dst_path, text)

        self._is_first_write = False
