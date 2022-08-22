from enum import Enum
from datetime import datetime, timedelta
from typing import Union

from .filter import Filter, FilterResult


def age_condition_applies(dt: datetime, age: timedelta, mode: str, reference: datetime):
    """
    Returns whether `dt` is older / newer (`mode`) than `age` as measured on `reference`
    """
    if mode not in ("older", "newer"):
        raise ValueError(mode)

    is_past = (dt + age).timestamp() < reference.timestamp()
    return (mode == "older") == is_past


class Mode(str, Enum):
    older = "older"
    newer = "newer"


class TimeFilter(Filter):

    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    mode: Mode = Mode.older

    _age: timedelta

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                    mode=str(self.mode),
                    reference=datetime.now(),
                )
        return match

    def pipeline(self, args: dict) -> FilterResult:
        dt = self.get_datetime(args)
        if dt is None:
            return FilterResult(matches=False, updates={})
        dt = dt.astimezone()

        match = self.matches_datetime(dt)
        return FilterResult(
            matches=match,
            updates={self.name: dt},
        )

    def get_datetime(self, args: dict) -> Union[datetime, None]:
        raise NotImplemented
