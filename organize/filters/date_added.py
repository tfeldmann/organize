import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from organize.filter import FilterConfig

from .common.timefilter import TimeFilter


def read_date_added(path: Path):
    cmd = ["mdls", "-name", "kMDItemDateAdded", "-raw", str(path)]
    out = subprocess.check_output(cmd, encoding="utf-8").strip()
    dt = datetime.strptime(out, "%Y-%m-%d %H:%M:%S %z")
    return dt


class DateAdded(TimeFilter):

    """Matches files by the time the file was added to a folder.

    **`date_added` is only available on macOS!**

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
        {date_added}: The datetime the files / folders were added.
    """

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="date_added",
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        if sys.platform != "darwin":
            raise EnvironmentError("date_added is only available on macOS")
        return super().__post_init__()

    def get_datetime(self, path: Path) -> datetime:
        return read_date_added(path)
