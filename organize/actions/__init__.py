from typing import Tuple, Type

from organize.action import Action

from .confirm import Confirm
from .copy import Copy
from .delete import Delete
from .echo import Echo
from .hardlink import Hardlink
from .macos_tags import MacOSTags
from .move import Move
from .python import Python
from .rename import Rename
from .shell import Shell
from .symlink import Symlink
from .trash import Trash
from .write import Write

ALL: Tuple[Type[Action], ...] = (
    Confirm,
    Copy,
    Delete,
    Echo,
    Hardlink,
    MacOSTags,
    Move,
    Python,
    Rename,
    Shell,
    Symlink,
    Trash,
    Write,
)
