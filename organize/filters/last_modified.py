from typing import Dict, Optional

import pendulum  # type: ignore
from organize.compat import Path
from organize.utils import DotDict

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
                  - LastModified
                actions:
                  - move: '~/Documents/PDF/{lastmodified.year}/'
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
    ) -> None:
        self._mode = mode.strip().lower()
        if self._mode not in ("older", "newer"):
            raise ValueError("Unknown option for 'mode': must be 'older' or 'newer'.")
        self.is_older = self._mode == "older"
        self.timedelta = pendulum.duration(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

    def pipeline(self, args: DotDict) -> Optional[Dict[str, pendulum.DateTime]]:
        file_modified = self._last_modified(args.path)
        # Pendulum bug: https://github.com/sdispater/pendulum/issues/387
        # in_words() is a workaround: total_seconds() returns 0 if years are given
        if self.timedelta.in_words():
            is_past = (file_modified + self.timedelta).is_past()
            match = self.is_older == is_past
        else:
            match = True
        if match:
            return {"lastmodified": file_modified}
        return None

    def _last_modified(self, path: Path) -> pendulum.DateTime:
        return pendulum.from_timestamp(float(path.stat().st_mtime))

    def __str__(self):
        return "[LastModified] All files last modified %s than %s" % (
            self._mode,
            self.timedelta.in_words(),
        )
