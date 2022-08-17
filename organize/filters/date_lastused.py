import subprocess
import sys
from datetime import datetime
from typing import Union

from fs.base import FS

from ._timefilter import TimeFilter


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

    name = "date_lastused"

    def get_datetime(self, args: dict) -> Union[datetime, None]:
        if sys.platform != "darwin":
            raise EnvironmentError("date_lastused is only available on macOS")

        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]

        cmd = ["mdls", "-name", "kMDItemLastUsedDate", "-raw", fs.getsyspath(fs_path)]
        out = subprocess.check_output(cmd, encoding="utf-8").strip()
        if out == "(null)":
            return None
        dt = datetime.strptime(out, "%Y-%m-%d %H:%M:%S %z")
        return dt

    def __str__(self):
        return "[DateLastUsed] All files / folders added %s than %s" % (
            self._mode,
            self.timedelta,
        )
