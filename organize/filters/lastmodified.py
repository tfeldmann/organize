from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

from organize.filter import FilterConfig

from .common.timefilter import TimeFilter


def read_lastmodified(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


class LastModified(TimeFilter):

    """Matches files by last modified date

    Attributes:
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

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="lastmodified",
        files=True,
        dirs=True,
    )

    def get_datetime(self, path: Path) -> datetime:
        return read_lastmodified(path)
