from datetime import datetime, timedelta
from typing import Union

from schema import Optional, Or

from .filter import Filter, FilterResult
from .utils import age_condition_applies


class TimeFilter(Filter):

    schema_support_instance_without_args = True
    arg_schema = {
        Optional("mode"): Or("older", "newer"),
        Optional("years"): int,
        Optional("months"): int,
        Optional("weeks"): int,
        Optional("days"): int,
        Optional("hours"): int,
        Optional("minutes"): int,
        Optional("seconds"): int,
    }

    def __init__(
        self,
        years=0,
        months=0,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        mode="older",
    ):
        self.age = timedelta(
            weeks=52 * years + 4 * months + weeks,  # quick and a bit dirty
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        self.mode = mode.strip().lower()
        if self.mode not in ("older", "newer"):
            raise ValueError("Unknown option for 'mode': must be 'older' or 'newer'.")

    def matches_datetime(self, dt: datetime) -> bool:
        match = True
        if self.age.total_seconds():
            if not dt:
                match = False
            else:
                match = age_condition_applies(
                    dt=dt,
                    age=self.age,
                    mode=self.mode,
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
            updates={self.get_name(): dt},
        )

    def get_datetime(self, args: dict) -> Union[datetime, None]:
        raise NotImplemented
