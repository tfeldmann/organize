from schema import Optional, Or
from datetime import datetime, timedelta
from typing import Dict, Optional as tyOptional

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

    name = "created"
    schema_support_instance_without_args = True
    arg_schema = {
        Optional("years"): int,
        Optional("months"): int,
        Optional("weeks"): int,
        Optional("days"): int,
        Optional("hours"): int,
        Optional("minutes"): int,
        Optional("seconds"): int,
        Optional("mode"): Or("older", "newer"),
    }

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
            weeks=52 * years + 4 * months + weeks,  # quick and a bit dirty
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

    def pipeline(self, args: dict) -> tyOptional[Dict[str, datetime]]:
        fs = args["fs"]
        fs_path = args["fs_path"]

        file_created: datetime
        file_created = fs.getinfo(fs_path, namespaces=["details"]).created
        if file_created:
            file_created = file_created.astimezone()

        if self.timedelta.total_seconds():
            if not file_created:
                match = False
            else:
                is_past = (
                    file_created + self.timedelta
                ).timestamp() < datetime.now().timestamp()
                match = self.should_be_older == is_past
        else:
            match = True
        if match:
            return {"created": file_created}
        return None

    def __str__(self):
        return "[Created] All files %s than %s" % (
            self._mode,
            self.timedelta,
        )
