import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from organize.filter import FilterConfig

from .common.timefilter import TimeFilter


def read_date_lastused(path: Path):
    cmd = ["mdls", "-name", "kMDItemLastUsedDate", "-raw", str(path)]
    out = subprocess.check_output(cmd, encoding="utf-8").strip()
    if out == "(null)":
        raise ValueError("date_lastused not available")
    return datetime.strptime(out, "%Y-%m-%d %H:%M:%S %z")


class DateLastUsed(TimeFilter):

    """Matches files by the time the file was last used.

    **`date_lastused` is only available on macOS!**

    Args:
        years (int): specify number of years
        months (int): specify number of months
        weeks (float): specify number of weeks
        days (float): specify number of days
        hours (float): specify number of hours
        minutes (float): specify number of minutes
        seconds (float): specify number of seconds
        mode (str):
            either 'older' or 'newer'. 'older' matches files / folders last used before
            the given time, 'newer' matches files / folders last used within the given
            time. (default = 'older')

    Returns:
        {date_lastused}: The datetime the files / folders were added.
    """

    filter_config: ClassVar = FilterConfig(
        name="date_lastused",
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        if sys.platform != "darwin":
            raise EnvironmentError("date_added is only available on macOS")
        return super().__post_init__()

    def get_datetime(self, path: Path) -> datetime:
        return read_date_lastused(path)
