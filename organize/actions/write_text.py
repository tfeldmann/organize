import logging
from typing import Union

from fs import errors, open_fs
from fs.base import FS
from fs.opener import manage_fs
from fs.opener.errors import OpenerError
from schema import Optional, Or

from organize.utils import SimulationFS, Template

from .action import Action
from .copymove_utils import basename, dirname, expand_args

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
        textfile = self.textfile.render(args)
        dst_path = textfile

        # TODO: Create helper function for this (maybe `sandboxed_fs_path(fs, path)`?)
        if self.filesystem:
            if isinstance(self.filesystem, str):
                dst_fs = expand_args(self.filesystem, args)
            else:
                dst_fs = self.filesystem
        else:
            dst_fs = dirname(dst_path)
            dst_path = basename(dst_path)
        try:
            dst_fs = open_fs(dst_fs, create=False, writeable=True)
        except (errors.CreateFailed, OpenerError):
            if not simulate:
                dst_fs = open_fs(dst_fs, create=True, writeable=True)
            else:
                dst_fs = SimulationFS(dst_fs)

        text = self.text.render(args)

        if self._is_first_write and self.clear_before_first_write:
            self.print(f"Clearing file {dst_path}")
            if not simulate:
                dst_fs.create(dst_path, wipe=True)

        self.print(f'{textfile}: {self.mode} "{text}"')
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
