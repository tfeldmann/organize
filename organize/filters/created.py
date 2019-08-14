import sys
from datetime import datetime, timedelta
from .filter import Filter


class Created(Filter):

    """
    Matches files by created date

    :param int days:
        specify number of days

    :param int hours:
        specify number of hours

    :param int minutes:
        specify number of minutes

    :param str mode:
        either 'older' or 'newer'. 'older' matches all files created before the given
        time, 'newer' matches all files created within the given time.
        (default = 'older')

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

    def run(self, attrs):
        created_date = self._created(attrs.path)
        reference_date = datetime.now() - self.timedelta
        match = (self.is_older and created_date <= reference_date) or (
            not self.is_older and created_date >= reference_date
        )
        if match:
            return {"created": created_date}

    def _created(self, path):
        # see https://stackoverflow.com/a/39501288/300783
        stat = path.stat()
        if sys.platform.startswith("win"):
            time = stat.st_ctime
        else:
            try:
                time = stat.st_birthtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                time = stat.st_mtime
        return datetime.fromtimestamp(time)

    def __str__(self):
        return "Created(delta=%s, select_mode=%s)" % (self.timedelta, self._mode)
