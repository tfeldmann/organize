import os
from pathlib import Path
from typing import ClassVar, Literal, assert_type

import arrow
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource

Period = Literal[
    "month",
    "day",
    "hour",
    "minute",
    "second",
]


@dataclass(config=ConfigDict(extra="forbid"))
class OnePer:
    """Group files by modification time.

    This filter finds files that were modified in a given time period, except
    for the earliest file from the time period.

    Attributes:
        detect_original_by (str):
            Detection method to distinguish between original and duplicate.
            Possible values are:

            - `"first_seen"`: Whatever file is visited first is the original. This
              depends on the order of your location entries.
            - `"name"`: The first entry sorted by name is the original.
            - `"created"`: The first entry sorted by creation date is the original.
            - `"lastmodified"`: The first file sorted by date of last modification is
               the original.

        period (str):
            The period to group files into.
            Possible values are:

            - `"second"`
            - `"minute"`
            - `"hour"`
            - `"day"`
            - `""`
    """

    period: Period = "hour"
    detect_the_one_by: str = "modified"

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="one_per", files=True, dirs=True
    )

    def __post_init__(self):
        assert_type(self.period, Period)

        self._seen_files: set["os.PathLike"] = set()
        self._the_one_for_period: dict["arrow.Arrow", "os.PathLike"] = dict()

    def get_period(self, file: Path) -> arrow.Arrow:
        ts = arrow.get(file.stat().st_mtime)
        return ts.floor(self.period)

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"

        if res.path.is_symlink():
            return False

        if res.path in self._seen_files:
            return False
        self._seen_files.add(res.path)

        period = self.get_period(res.path)
        self._the_one_for_period[period] = res.path

        return False
