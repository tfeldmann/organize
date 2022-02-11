import subprocess
from datetime import datetime, timezone
from typing import Union

from fs.base import FS

from ._timefilter import TimeFilter


class Created(TimeFilter):
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

    def get_datetime(self, args) -> Union[None, datetime]:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        created = fs.getinfo(fs_path, namespaces=["details"]).created
        if not created:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we try to use the stat utility.
            created = self.fallback_method(fs, fs_path)
        return created

    def fallback_method(self, fs, fs_path):
        if fs.hassyspath(fs_path):
            syspath = fs.getsyspath(fs_path)
            commands = (
                ["stat", "--format=%W", syspath],  # GNU coreutils
                ["stat", "-f %B", syspath],  # BSD
            )
            for cmd in commands:
                try:
                    created_str = subprocess.run(
                        cmd, capture_output=True, check=True, encoding="utf-8"
                    ).stdout.strip()
                    timestamp = int(created_str)
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except subprocess.CalledProcessError:
                    pass
        raise EnvironmentError("File creation time is not available.")

    def __str__(self):
        return "[Created] All files / folders %s than %s" % (
            self._mode,
            self.timedelta,
        )
