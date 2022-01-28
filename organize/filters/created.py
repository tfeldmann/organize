from datetime import datetime, timedelta

from fs.base import FS
from schema import Optional, Or  # type: ignore

from .filter import Filter, FilterResult


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
            either 'older' or 'newer'. 'older' matches all files created before the given
            time, 'newer' matches all files created within the given time.
            (default = 'older')

    Returns:
        {created}: The datetime the file / dir was created.
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
    ) -> None:
        self._mode = mode.strip().lower()
        if self._mode not in ("older", "newer"):
            raise ValueError("Unknown option for 'mode': must be 'older' or 'newer'.")
        self.should_be_older = self._mode == "older"
        self.timedelta = timedelta(
            weeks=52 * years + 4 * months + weeks,  # quick and a bit dirty
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]

        file_created: Optional[datetime]
        file_created = fs.getinfo(fs_path, namespaces=["details"]).created
        if file_created:
            file_created = file_created.astimezone()

        if self.timedelta.total_seconds():
            if not file_created:
                match = False
            else:
                is_past = (
                    file_created + self.timedelta
                ).timestamp() < datetime.now().timestamp()
                match = self.should_be_older == is_past
        else:
            match = True

        return FilterResult(
            matches=match,
            updates={self.get_name(): file_created},
        )

    def __str__(self):
        return "[Created] All files %s than %s" % (
            self._mode,
            self.timedelta,
        )
