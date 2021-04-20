import sys
from typing import Dict, Optional, SupportsFloat

import pendulum  # type: ignore
from pathlib import Path
from organize.utils import DotDict

from .filter import Filter


class Created(Filter):

    """
    Matches files by created date

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
        either 'older' or 'newer'. 'older' matches all files created before the given
        time, 'newer' matches all files created within the given time.
        (default = 'older')

    :param str timezone:
        specify timezone

    :returns:
        - ``{created.year}`` -- the year the file was created
        - ``{created.month}`` -- the month the file was created
        - ``{created.day}`` -- the day the file was created
        - ``{created.hour}`` -- the hour the file was created
        - ``{created.minute}`` -- the minute the file was created
        - ``{created.second}`` -- the second the file was created

    Examples:
        - Show all files on your desktop created at least 10 days ago:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - created:
                      days: 10
                actions:
                  - echo: 'Was created at least 10 days ago'

        - Show all files on your desktop which were created within the last 5 hours:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - created:
                      hours: 5
                      mode: newer
                actions:
                  - echo: 'Was created within the last 5 hours'

        - Sort pdfs by year of creation:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Documents'
                filters:
                  - extension: pdf
                  - created
                actions:
                  - move: '~/Documents/PDF/{created.year}/'

        - Use specific timezone when processing files

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Documents'
                filters:
                  - extension: pdf
                  - created:
                      timezone: "Europe/Moscow"
                actions:
                  - move: '~/Documents/PDF/{created.day}/{created.hour}/'
    """

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
        timezone=pendulum.tz.local_timezone(),
    ) -> None:
        self._mode = mode.strip().lower()
        if self._mode not in ("older", "newer"):
            raise ValueError("Unknown option for 'mode': must be 'older' or 'newer'.")
        self.is_older = self._mode == "older"
        self.timezone = timezone
        self.timedelta = pendulum.duration(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        print(bool(self.timedelta))

    def pipeline(self, args: DotDict) -> Optional[Dict[str, pendulum.DateTime]]:
        created_date = self._created(args.path)
        # Pendulum bug: https://github.com/sdispater/pendulum/issues/387
        # in_words() is a workaround: total_seconds() returns 0 if years are given
        if self.timedelta.in_words():
            is_past = (created_date + self.timedelta).is_past()
            match = self.is_older == is_past
        else:
            match = True
        if match:
            return {"created": created_date}
        return None

    def _created(self, path: Path) -> pendulum.DateTime:
        # see https://stackoverflow.com/a/39501288/300783
        stat = path.stat()
        time = 0  # type: SupportsFloat
        if sys.platform.startswith("win"):
            time = stat.st_ctime
        else:
            try:
                time = stat.st_birthtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                time = stat.st_mtime
        return pendulum.from_timestamp(float(time), tz=self.timezone)

    def __str__(self):
        return "[Created] All files %s than %s" % (
            self._mode,
            self.timedelta.in_words(),
        )
