from .copy import Copy
from .delete import Delete
from .echo import Echo
from .macos_tags import MacOSTags
from .move import Move
from .python import Python
from .rename import Rename
from .shell import Shell
from .trash import Trash

ALL = {
    "copy": Copy,
    "delete": Delete,
    "echo": Echo,
    "macos_tags": MacOSTags,
    "move": Move,
    "python": Python,
    "rename": Rename,
    "shell": Shell,
    "trash": Trash,
}
