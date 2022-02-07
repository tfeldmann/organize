from datetime import datetime, timedelta
from typing import Union

from fs.base import FS
from schema import Optional, Or

from .filter import Filter, FilterResult
from .utils import age_condition_applies


class Created(Filter):
    """Matches files / folders by created date

    Args:
        years (int): specify number of years
        months (int): specify number of months
        weeks (float): specify number of weeks
        days (float): specify number of days
        hours (float): specify number of hours
        minutes (float): specify number of minutes
        seconds (float): specify number of seconds
        mode (str):
            either 'older' or 'newer'. 'older' matches files / folders created before the given
            time, 'newer' matches files / folders created within the given time.
            (default = 'older')

    Returns:
        {created}: The datetime the file / folder was created.
    """

    name = "created"
    schema_support_instance_without_args = True
    arg_schema = {
        Optional("years"): int,
        Optional("months"): int,
        Optional("weeks"): int,
        Optional("days"): int,
        Optional("hours"): int,
        Optional("minutes"): int,
        Optional("seconds"): int,
        Optional("mode"): Or("older", "newer"),
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

    def matches_created_time(self, created: Union[None, datetime]):
        match = True
        if self.age.total_seconds():
            if not created:
                match = False
            else:
                match = age_condition_applies(
                    dt=created,
                    age=self.age,
                    mode=self.mode,
                    reference=datetime.now(),
                )
        return match

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]

        created = fs.getinfo(fs_path, namespaces=["details"]).created
        if created:
            created = created.astimezone()

        match = self.matches_created_time(created)
        return FilterResult(
            matches=match,
            updates={self.get_name(): created},
        )

    def __str__(self):
        return "[Created] All files / folders %s than %s" % (
            self._mode,
            self.timedelta,
        )
