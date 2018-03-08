from datetime import datetime, timedelta
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
        the given time.

    Examples:
        - Show all files on your desktop last modified at least 10 days ago:

          .. code-block:: yaml

            # config.yaml
            rules:
              - folders: '~/Desktop'
                filters:
                  - LastModified:
                      - days: 10
                actions:
                  - Echo: 'Was modified at least 10 days ago'

        - Show all files on your desktop which were modified within the last
          5 hours:

          .. code-block:: yaml

            # config.yaml
            rules:
              - folders: '~/Desktop'
                filters:
                  - LastModified:
                      - hours: 5
                      - mode: newer
                actions:
                  - Echo: 'Was modified within the last 5 hours'
    """

    def __init__(self, days=0, hours=0, minutes=0, seconds=0, mode='older'):
        self._mode = mode.strip().lower()
        if self._mode not in ('older', 'newer'):
            raise ValueError(
                "Unknown option for 'mode': must be 'older' or 'newer'.")
        else:
            self.is_older = (self._mode == 'older')
        self.timedelta = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds)

    def matches(self, path):
        file_modified = self._last_modified(path)
        reference_date = datetime.now() - self.timedelta
        if self.is_older:
            return file_modified <= reference_date
        else:
            return file_modified >= reference_date

    def parse(self, path):
        file_modified = self._last_modified(path)
        return {'last_modified': file_modified}

    def _last_modified(self, path):
        return datetime.fromtimestamp(path.stat().st_mtime)

    def __str__(self):
        return 'FileModified(delta=%s, select_mode=%s)' % (
            self.timedelta, self._mode)
