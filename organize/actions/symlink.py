import logging
import os

from fs import path
from fs.base import FS
from fs.osfs import OSFS

from organize.utils import Template

from .action import Action

logger = logging.getLogger(__name__)


class Symlink(Action):

    """Create a symbolic link.

    Args:
        dest (str):
            The symlink destination. If **dest** ends with a slash `/``, create the
            symlink in the given directory. Can contain placeholders.

    Only the local filesystem is supported.
    """

    name = "symlink"

    def __init__(self, dest):
        self._dest = Template.from_string(dest)

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str

        if not isinstance(fs, OSFS):
            raise EnvironmentError("Symlinks only work on the local filesystem.")

        dest = os.path.expanduser(self._dest.render(**args))
        if dest.endswith("/"):
            dest = path.join(dest, path.basename(fs_path))

        self.print("Creating symlink: %s" % dest)
        if not simulate:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.symlink(fs.getsyspath(fs_path), dest)
