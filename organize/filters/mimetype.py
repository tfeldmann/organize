import mimetypes
from typing import ClassVar

from pydantic import Field
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.validators import FlatList


def guess_mimetype(path):
    type_, _ = mimetypes.guess_type(path, strict=False)
    return type_


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class MimeType:

    """Filter by MIME type associated with the file extension.

    Supports a single string or list of MIME type strings as argument.
    The types don't need to be fully specified, for example "audio" matches everything
    from "audio/midi" to "audio/quicktime".

    You can see a list of known MIME types on your system by running this oneliner:

    ```sh
    python3 -m organize.filters.mimetype
    ```

    Args:
        *mimetypes (list(str) or str): The MIME types to filter for.

    **Returns:**

    - `{mimetype}`: The MIME type of the file.
    """

    mimetypes: FlatList[str] = Field(default_factory=list)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="mimetype",
        files=True,
        dirs=False,
    )

    def matches(self, mimetype) -> bool:
        if mimetype is None:
            return False
        if not self.mimetypes:
            return True
        return any(mimetype.startswith(x) for x in self.mimetypes)

    def pipeline(self, res: Resource, output: Output) -> bool:
        mimetype = guess_mimetype(res.path)
        res.vars[self.filter_config.name] = mimetype
        return self.matches(mimetype)


if __name__ == "__main__":
    all_types = set(mimetypes.common_types.values()) | set(mimetypes.types_map.values())
    for t in sorted(all_types):
        print(t)
