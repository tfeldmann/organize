from .created import Created
from .duplicate import Duplicate
from .exif import Exif
from .extension import Extension
from .filecontent import FileContent
from .filename import Filename
from .filesize import FileSize
from .lastmodified import LastModified
from .mimetype import MimeType
from .python import Python
from .regex import Regex

ALL = {
    Created.name: Created,
    Duplicate.name: Duplicate,
    Exif.name: Exif,
    Extension.name: Extension,
    FileContent.name: FileContent,
    Filename.name: Filename,
    FileSize.name: FileSize,
    LastModified.name: LastModified,
    MimeType.name: MimeType,
    Python.name: Python,
    Regex.name: Regex,
}
