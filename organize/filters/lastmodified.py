from datetime import datetime, timedelta
from typing import Union

from fs.base import FS
from schema import Optional, Or

from .filter import Filter, FilterResult
from .utils import age_condition_applies


class LastModified(Filter):

    """Matches files by last modified date

    Args:
        years (int): specify number of years
        months (int): specify number of months
        weeks (float): specify number of weeks
        days (float): specify number of days
        hours (float): specify number of hours
        minutes (float): specify number of minutes
        seconds (float): specify number of seconds
        mode (str):
            either 'older' or 'newer'. 'older' matches files / folders last modified before
            the given time, 'newer' matches files / folders last modified within the given
            time. (default = 'older')

    Returns:
        {lastmodified}: The datetime the files / folders was lastmodified.
    """

    name = "lastmodified"
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

    def matches_lastmodified_time(self, lastmodified: Union[None, datetime]):
        match = True
        if self.age.total_seconds():
            if not lastmodified:
                match = False
            else:
                match = age_condition_applies(
                    dt=lastmodified,
                    age=self.age,
                    mode=self.mode,
                    reference=datetime.now(),
                )
        return match

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]

        modified = fs.getmodified(fs_path)
        if modified:
            modified = modified.astimezone()

        match = self.matches_lastmodified_time(modified)
        return FilterResult(
            matches=match,
            updates={self.get_name(): modified},
        )

    def __str__(self):
        return "[LastModified] All files / folders last modified %s than %s" % (
            self._mode,
            self.timedelta,
        )
