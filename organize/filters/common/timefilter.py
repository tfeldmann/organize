from datetime import datetime, timedelta
from enum import Enum
from typing import ClassVar, Literal, Union

from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


class Mode(Enum):
    older = "older"
    newer = "newer"


def age_condition_applies(
    dt: datetime, age: timedelta, mode: Mode, reference: datetime
):
    """
    Returns whether `dt` is older / newer (`mode`) than `age` as measured on `reference`
    """
    is_past = (dt + age).timestamp() < reference.timestamp()
    return (mode == Mode.older) == is_past


@dataclass
class TimeFilter:
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    mode: Literal["older", "newer"] = "older"

    filter_config: ClassVar = FilterConfig("timefilter", files=True, dirs=False)

    def __post_init__(self):
        self._age = timedelta(
            weeks=52 * self.years
            + 4 * self.months
            + self.weeks,  # quick and a bit dirty
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
        )

    def matches_datetime(self, dt: datetime) -> bool:
        match = True
        if self._age.total_seconds():
            if not dt:
                match = False
            else:
                match = age_condition_applies(
                    dt=dt,
                    age=self._age,
                    mode=self.mode,
                    reference=datetime.now(),
                )
        return match

    def pipeline(self, res: Resource, output: Output) -> bool:
        dt = self.get_datetime(res.path)
        if dt is None:
            return False
        dt = dt.astimezone()
        match = self.matches_datetime(dt)
        if match:
            res.vars[self.filter_config.name] = dt
            return True
        return False

    def get_datetime(self, args: dict) -> Union[datetime, None]:
        raise NotImplementedError
