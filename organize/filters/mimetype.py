from pydantic import Field
import mimetypes
from typing import List, Union

from typing_extensions import Literal

from organize.utils import flatten
from organize.validators import ensure_list

from .filter import Filter, FilterResult


def guess_mimetype(path):
    type_, _ = mimetypes.guess_type(path, strict=False)
    return type_


class MimeType(Filter):

    """Filter by MIME type associated with the file extension.

    Supports a single string or list of MIME type strings as argument.
    The types don't need to be fully specified, for example "audio" matches everything
    from "audio/midi" to "audio/quicktime".

    You can see a list of known MIME types on your system by running this oneliner:

    ```sh
    python3 -c "import mimetypes as m; print('\\n'.join(sorted(set(m.common_types.values()) | set(m.types_map.values()))))"
    ```

    Args:
        *mimetypes (list(str) or str): The MIME types to filter for.

    **Returns:**

    - `{mimetype}`: The MIME type of the file.
    """

    name: Literal["mimetype"] = Field("mimetype", repr=False)
    mimetypes: Union[List[str], str] = Field(default_factory=list)

    class Config:
        anystr_lower = True

    class ParseConfig:
        accepts_positional_arg = "mimetypes"

    _validate_mimetypes = ensure_list("mimetypes")

    def matches(self, mimetype) -> bool:
        if mimetype is None:
            return False
        if not self.mimetypes:
            return True
        return any(mimetype.startswith(x) for x in self.mimetypes)

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            raise ValueError("Dirs not supported.")
        mimetype = guess_mimetype(fs_path)
        return FilterResult(
            matches=self.matches(mimetype),
            updates={self.name: mimetype},
        )
