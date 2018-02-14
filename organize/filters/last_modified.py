from datetime import datetime, timedelta
from .filter import Filter


class LastModified(Filter):

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
