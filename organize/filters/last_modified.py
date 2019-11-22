from datetime import datetime, timedelta
from typing import Dict, Optional

from organize.compat import Path
from organize.utils import DotDict

from .filter import Filter


class LastModified(Filter):

    """
    Matches files by last modified date

    :param int days:
        specify number of days

    :param int hours:
        specify number of hours

    :param int minutes:
        specify number of minutes

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

    def __init__(self, days=0, hours=0, minutes=0, seconds=0, mode="older"):
        self._mode = mode.strip().lower()
        if self._mode not in ("older", "newer"):
            raise ValueError("Unknown option for 'mode': must be 'older' or 'newer'.")
        else:
            self.is_older = self._mode == "older"
        self.timedelta = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )

    def pipeline(self, args: DotDict) -> Optional[Dict[str, datetime]]:
        file_modified = self._last_modified(args.path)
        reference_date = datetime.now() - self.timedelta
        match = (self.is_older and file_modified <= reference_date) or (
            not self.is_older and file_modified >= reference_date
        )
        if match:
            return {"lastmodified": file_modified}
        return None

    def _last_modified(self, path: Path) -> datetime:
        return datetime.fromtimestamp(path.stat().st_mtime)

    def __str__(self) -> str:
        return "FileModified(delta=%s, select_mode=%s)" % (self.timedelta, self._mode)
