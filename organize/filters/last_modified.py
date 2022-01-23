from datetime import datetime, timedelta
from optparse import Option
from time import time
from typing import Dict, Optional

from .filter import Filter


class LastModified(Filter):

    """
    Matches files by last modified date

    :param int years:
        specify number of years

    :param int months:
        specify number of months

    :param float weeks:
        specify number of weeks

    :param float days:
        specify number of days

    :param float hours:
        specify number of hours

    :param float minutes:
        specify number of minutes

    :param float seconds:
        specify number of seconds

    :param str mode:
        either 'older' or 'newer'. 'older' matches all files last modified
        before the given time, 'newer' matches all files last modified within
        the given time. (default = 'older')

    :returns:
        - ``{lastmodified.year}`` -- the year the file was last modified
        - ``{lastmodified.month}`` -- the month the file was last modified
        - ``{lastmodified.day}`` -- the day the file was last modified
        - ``{lastmodified.hour}`` -- the hour the file was last modified
        - ``{lastmodified.minute}`` -- the minute the file was last modified
        - ``{lastmodified.second}`` -- the second the file was last modified

    Examples:
        - Show all files on your desktop last modified at least 10 days ago:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - lastmodified:
                      days: 10
                actions:
                  - echo: 'Was modified at least 10 days ago'

        - Show all files on your desktop which were modified within the last
          5 hours:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - lastmodified:
                      hours: 5
                      mode: newer
                actions:
                  - echo: 'Was modified within the last 5 hours'

        - Sort pdfs by year of last modification

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Documents'
                filters:
                  - extension: pdf
                  - lastmodified
                actions:
                  - move: '~/Documents/PDF/{lastmodified.year}/'
    """

    name = "lastmodified"

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
            weeks=years * 52 + months * 4 + weeks,  # quick and a bit dirty
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

    def pipeline(self, args: dict) -> Optional[Dict[str, datetime]]:
        fs = args["fs"]
        fs_path = args["fs_path"]
        file_modified: datetime
        file_modified = fs.getmodified(fs_path)
        if file_modified:
            file_modified = file_modified.astimezone()
        if self.timedelta.total_seconds():
            if not file_modified:
                match = False
            else:
                is_past = (
                    file_modified + self.timedelta
                ).timestamp() < datetime.now().timestamp()
                match = self.should_be_older == is_past
        else:
            match = True
        if match:
            return {"lastmodified": file_modified}
        return None

    def __str__(self):
        return "[LastModified] All files last modified %s than %s" % (
            self._mode,
            self.timedelta,
        )

    @classmethod
    def schema(cls):
        from schema import Optional, Or

        return Or(
            cls.name,
            {
                Optional(cls.name): {
                    Optional("mode"): Or("older", "newer"),
                    Optional("years"): int,
                    Optional("months"): int,
                    Optional("weeks"): int,
                    Optional("days"): int,
                    Optional("hours"): int,
                    Optional("minutes"): int,
                    Optional("seconds"): int,
                }
            },
        )
