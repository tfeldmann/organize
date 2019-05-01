from datetime import datetime, timedelta
from .filter import Filter
import re
import os


class Filesize(Filter):
    """
    Matches files by last modified date

    :param str smaller:
        Will match files having a size equal to or smaller than specified size.

        Valid format examples: ``1g``, ``4G``, ``1.5MB``, ``5000`` The if no unit is given, bytes is assumed.
        Use ``bigger: 1`` to test for empty files.

    :param str bigger:
        Will match files having a size equal equal to or bigger than specified size.

    Combined use of both parameters in a single Filesize filter will only match if the file satisfies both conditions.

    :returns:
        - ``{filesize}`` -- File size in bytes

    Examples:
        - Trash big downloads:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Downloads'
                filters:
                  - Filesize:
                      - bigger: 500m
                actions:
                  - Trash

    """

    @staticmethod
    def _parse_size_arg(size_string):
        size_string = size_string.lower().strip()
        size_number = re.findall(r"^([0-9\.]+)", size_string)[0]
        size_unit = re.findall(r"([a-z]+)$", size_string)
        if len(size_unit) > 0:
            size_unit = size_unit[0]
        else:
            size_unit = "b"
        unit_lookup = {"b": 0, "k": 3, "m": 6, "g": 9, "t": 12, "p": 15}
        return float(size_number) * pow(10, unit_lookup[size_unit.strip().lower()[0]])

    def __init__(self, smaller=None, bigger=None):
        if smaller is not None:
            smaller = self._parse_size_arg(smaller)
        if bigger is not None:
            bigger = self._parse_size_arg(bigger)

        self.smaller = smaller
        self.bigger = bigger

    def matches(self, path):
        file_size = self._get_file_size(path)
        return (self.smaller is None or (file_size <= self.smaller)) and (
            self.bigger is None or (file_size >= self.bigger)
        )

    def parse(self, path):
        file_size = self._get_file_size(path)
        return {"filesize": file_size}

    def _get_file_size(self, path):
        return os.path.getsize(path)

    def __str__(self):
        return f"FileSize({self.bigger} <= filesize <= {self.smaller})"
