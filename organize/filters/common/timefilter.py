import logging
from datetime import datetime, tzinfo
from pathlib import Path
from typing import ClassVar, Literal, Union

import arrow
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(extra="forbid", arbitrary_types_allowed=True))
class TimeFilter:
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    mode: Literal["older", "newer"] = "older"
    timezone: Union[tzinfo, str] = "local"

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        "timefilter",
        files=True,
        dirs=False,
    )

    def __post_init__(self):
        self._has_comparison = (
            self.years
            or self.months
            or self.weeks
            or self.days
            or self.hours
            or self.minutes
            or self.seconds
        )
        self._comparison_dt = (
            arrow.now()
            .shift(
                years=-self.years,
                months=-self.months,
                weeks=-self.weeks,
                days=-self.days,
                hours=-self.hours,
                minutes=-self.minutes,
                seconds=-self.seconds,
            )
            .datetime
        )

    def matches_datetime(self, dt: datetime) -> bool:
        if not self._has_comparison:
            return True

        if self.mode == "older":
            return dt < self._comparison_dt
        elif self.mode == "newer":
            return dt > self._comparison_dt
        else:
            raise ValueError(f"Unknown mode {self.mode}")

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        try:
            dt = self.get_datetime(res.path)
        except Exception as e:
            logging.warn(f"Cannot read datetime ({e})")
            return False

        # apply timezone
        dt = arrow.get(dt).to(self.timezone).datetime

        res.vars[self.filter_config.name] = dt
        return self.matches_datetime(dt)

    def get_datetime(self, path: Path) -> datetime:
        raise NotImplementedError()
