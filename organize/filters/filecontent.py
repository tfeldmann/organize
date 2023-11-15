import logging
import re
from typing import Any, ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class FileContent:
    """Matches file content with the given regular expression

    Args:
        expr (str): The regular expression to be matched.

    Any named groups (`(?P<groupname>.*)`) in your regular expression will
    be returned like this:

    **Returns:**

    - `{filecontent.groupname}`: The text matched with the named group
      `(?P<groupname>)`
    """

    expr: str = r"(?P<all>.*)"

    filter_config: ClassVar = FilterConfig(name="filecontent", files=True, dirs=False)

    def __post_init__(self):
        self._expr = re.compile(self.expr, re.MULTILINE | re.DOTALL)

    def matches(self, path: str) -> Any:
        try:
            import textract

            content = textract.process(str(path), errors="ignore")
            match = self._expr.search(content.decode("utf-8", errors="ignore"))
            return match
        except ImportError as e:
            raise ImportError(
                "textract is not installed. "
                "Install with pip install organize-tool[textract]"
            ) from e
        except textract.exceptions.CommandLineError as e:
            logging.exception(e)

    def pipeline(self, res: Resource, output: Output) -> bool:
        match = self.matches(path=res.path)

        if match:
            res.deep_merge(self.filter_config.name, match.groupdict())
        return bool(match)
