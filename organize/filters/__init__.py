from typing import Union

import pydantic
from typing_extensions import Annotated

from .created import Created
from .date_added import DateAdded
from .date_lastused import DateLastUsed

# from .duplicate import Duplicate
from .empty import Empty

# from .exif import Exif
from .extension import Extension

# from .filecontent import FileContent
from .filter import Filter

# from .hash import Hash
from .lastmodified import LastModified

# from .macos_tags import MacOSTags
# from .mimetype import MimeType
from .name import Name

# from .python import Python
# from .regex import Regex
from .size import Size

FilterType = Union[
    Filter,
    Annotated[
        Union[
            Name,
            Empty,
            Created,
            DateAdded,
            DateLastUsed,
            LastModified,
            Extension,
            Size,
        ],
        pydantic.Field(discriminator="name"),
    ],
]
