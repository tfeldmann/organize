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

    :param str select:
        either 'within' or 'before'. 'within' matches all file last modified
        within the given time, 'before' all files last modified before the given
        time.

    Examples:
        - Show all files on your desktop modified within the last 10 days:

          .. code-block:: yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - LastModified:
                      - days: 10
                actions:
                  - Echo: 'Was modified within the last 10 days'

        - Show all files on your desktop which were modified at least 5 hours
          ago:

          .. code-block:: yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - LastModified:
                      - hours: 5
                      - select: 'before'
                actions:
                  - Echo: 'Was modified more than 5 hours ago.'
    """

    def __init__(self, days=0, hours=0, minutes=0, seconds=0, select='within'):
        _select = select.strip().lower()
        if _select not in ('within', 'before'):
            raise Exception("Unknown option for 'select': must be 'within' or 'before'.")
        else:
            self.select_before = (_select == 'before')
        delta = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds)
        self.reference_date = datetime.now() - delta

    def matches(self, path):
        file_modified = self._last_modified(path)
        if self.select_before:
            return file_modified <= self.reference_date
        else:
            return file_modified >= self.reference_date

    def parse(self, path):
        file_modified = self._last_modified(path)
        return {'last_modified': file_modified}

    def _last_modified(self, path):
        return datetime.fromtimestamp(path.stat().st_mtime)
