from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(extra="forbid"))
class Empty:

    """Finds empty dirs and files"""

    filter_config: ClassVar = FilterConfig(name="empty", files=True, dirs=True)

    def pipeline(self, res: Resource, output: Output) -> bool:
        return res.is_empty()
