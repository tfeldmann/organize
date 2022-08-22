import subprocess
from datetime import datetime, timezone

from fs.base import FS
from typing_extensions import Literal

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

    name: Literal["created"] = "created"

    def get_datetime(self, args) -> datetime:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        created = fs.getinfo(fs_path, namespaces=["details"]).created
        if not created:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we try to use the stat utility.
            created = self.fallback_method(fs, fs_path)
        if not created:
            raise EnvironmentError("File creation time is not available.")
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
                    created_str = subprocess.check_output(cmd, encoding="utf-8").strip()
                    timestamp = int(created_str)
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except subprocess.CalledProcessError:
                    pass
