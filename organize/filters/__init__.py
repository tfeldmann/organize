from .created import Created
from .duplicate import Duplicate
from .exif import Exif
from .extension import Extension
from .file_content import FileContent
from .filename import Filename
from .filesize import FileSize
from .last_modified import LastModified
from .mimetype import MimeType
from .python import Python
from .regex import Regex

ALL = {
    "created": Created,
    "duplicate": Duplicate,
    "exif": Exif,
    "extension": Extension,
    "file_content": FileContent,
    "filename": Filename,
    "filesize": FileSize,
    "last_modified": LastModified,
    "mimetype": MimeType,
    "python": Python,
    "regex": Regex,
}
