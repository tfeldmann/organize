import logging
from typing import Union

from fs.base import FS
from fs import open_fs
from schema import Optional, Or

from .copymove_utils import expand_args, dirname, basename
from organize.utils import Template

from .action import Action

logger = logging.getLogger(__name__)


class AppendText(Action):

    """Append text to a file."""

    name = "append_text"
    arg_schema = Or(
        {
            "text": str,
            "textfile": str,
            Optional("newline"): bool,
            Optional("filesystem"): object,
        },
    )

    def __init__(
        self,
        text: str,
        textfile: str,
        newline: bool = True,
        filesystem: Union[str, FS] = "",
    ) -> None:
        self.textfile = Template.from_string(textfile)
        self.text = Template.from_string(text)
        self.newline = newline
        self.filesystem = filesystem

    def pipeline(self, args: dict, simulate: bool):
        dst_path = self.textfile.render(args)
        # TODO: Create helper function for this
        # maybe `sandboxed_fs_path(fs, path)`?
        if self.filesystem:
            if isinstance(self.filesystem, str):
                dst_fs = expand_args(self.filesystem, args)
            else:
                dst_fs = self.filesystem
        else:
            dst_fs = dirname(dst_path)
            dst_path = basename(dst_path)
        with open_fs(dst_fs) as loc:
            text = self.text.render(args) + ("\n" if self.newline else "")
            loc.appendtext(dst_path, text)
