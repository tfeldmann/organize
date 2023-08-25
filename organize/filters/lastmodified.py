from datetime import datetime

from fs.base import FS

from ._timefilter import TimeFilter


class LastModified(TimeFilter):

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

    def get_datetime(self, args: dict) -> datetime:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        modified = fs.getmodified(fs_path)
        if not modified:
            raise EnvironmentError("lastmodified date is not available")
        return modified

    def __str__(self):
        return "[LastModified] All files / folders last modified %s than %s" % (
            self._mode,
            self.timedelta,
        )
