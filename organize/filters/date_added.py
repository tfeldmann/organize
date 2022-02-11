import subprocess
import sys
from datetime import datetime
from typing import Union

from fs.base import FS

from ._timefilter import TimeFilter


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

    name = "date_added"

    def get_datetime(self, args) -> Union[None, datetime]:
        if sys.platform != "darwin":
            raise EnvironmentError("date_added is only available on macOS")

        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]

        out = subprocess.run(
            ["mdls", "-name", "kMDItemDateAdded", "-raw", fs.getsyspath(fs_path)],
            capture_output=True,
            encoding="utf-8",
            check=True,
        ).stdout
        dt = datetime.strptime(out, "%Y-%m-%d %H:%M:%S %z")
        return dt

    def __str__(self):
        return "[DateAdded] All files / folders added %s than %s" % (
            self._mode,
            self.timedelta,
        )
