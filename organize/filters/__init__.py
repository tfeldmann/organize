from .created import Created
from .duplicate import Duplicate
from .exif import Exif
from .extension import Extension
from .filecontent import FileContent
from .lastmodified import LastModified
from .mimetype import MimeType
from .name import Name
from .python import Python
from .regex import Regex
from .size import Size

ALL = {
    Created.name: Created,
    Duplicate.name: Duplicate,
    Exif.name: Exif,
    Extension.name: Extension,
    FileContent.name: FileContent,
    Name.name: Name,
    Size.name: Size,
    LastModified.name: LastModified,
    MimeType.name: MimeType,
    Python.name: Python,
    Regex.name: Regex,
}
