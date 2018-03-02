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

    :param str select_mode:
        either 'min' or 'max'. 'min' matches all files last modified before the
        given time, 'max' matches all files last modified within the given
        time.

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
                      - select_mode: 'max'
                actions:
                  - Echo: 'Was modified within the last 5 hours'
    """

    def __init__(self, days=0, hours=0, minutes=0, seconds=0,
                 select_mode='min'):
        self._select_mode = select_mode.strip().lower()
        if self._select_mode not in ('min', 'max'):
            raise ValueError(
                "Unknown option for 'select_mode': must be 'min' or 'max'.")
        else:
            self.is_minimum = (self._select_mode == 'min')
        self.timedelta = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds)

    def matches(self, path):
        file_modified = self._last_modified(path)
        reference_date = datetime.now() - self.timedelta
        if self.is_minimum:
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
            self.timedelta, self._select_mode)
