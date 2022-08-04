import logging
from typing import Union

from fs.base import FS
from fs import open_fs
from schema import Optional, Or

from .copymove_utils import expand_args, dirname, basename
from organize.utils import Template

from .action import Action

logger = logging.getLogger(__name__)

MODES = (
    "prepend",
    "append",
    "overwrite",
)


class WriteText(Action):

    """Write text to a file.

    If the specified path does not exist it will be created.

    Args:
        text (str):
            The text that should be written. Supports templates.

        textfile (str):
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

    name = "write_text"
    arg_schema = Or(
        {
            "text": str,
            "textfile": str,
            Optional("mode"): Or(*MODES),
            Optional("newline"): bool,
            Optional("clear_before_first_write"): bool,
            Optional("filesystem"): object,
        },
    )

    def __init__(
        self,
        text: str,
        textfile: str,
        mode: str = "append",
        newline: bool = True,
        clear_before_first_write: bool = False,
        filesystem: Union[str, FS] = "",
    ) -> None:
        self.text = Template.from_string(text)
        self.textfile = Template.from_string(textfile)
        self.mode = mode.lower()
        self.clear_before_first_write = clear_before_first_write
        self.newline = newline
        self.filesystem = filesystem

        self._is_first_write = True

        if self.mode not in MODES:
            raise ValueError("mode must be one of %s" % ", ".join(MODES))

    def pipeline(self, args: dict, simulate: bool):
        dst_path = self.textfile.render(args)

        # TODO: Create helper function for this (maybe `sandboxed_fs_path(fs, path)`?)
        if self.filesystem:
            if isinstance(self.filesystem, str):
                dst_fs = expand_args(self.filesystem, args)
            else:
                dst_fs = self.filesystem
        else:
            dst_fs = dirname(dst_path)
            dst_path = basename(dst_path)

        text = self.text.render(args)

        with open_fs(dst_fs) as loc:
            if self._is_first_write and self.clear_before_first_write:
                self.print(f"Clearing file {dst_path}")
                if not simulate:
                    loc.writetext(dst_path, "")

            self.print(f'{dst_path}: {self.mode} "{text}"')
            if self.newline:
                text += "\n"

            if not simulate:
                if self.mode == "append":
                    loc.appendtext(dst_path, text)
                elif self.mode == "prepend":
                    content = loc.readtext(dst_path)
                    loc.writetext(dst_path, text + content)
                elif self.mode == "overwrite":
                    loc.writetext(dst_path, text)

            self._is_first_write = False
