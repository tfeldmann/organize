from datetime import datetime, timedelta
from .filter import Filter
import re
import os


class FileSize(Filter):
    """
    Matches files by last modified date

    :param str smaller:
        Will match files smaller than specified size. Valid format examples: 1g, 4Gb, 1.5MB

    :param str bigger:
        Will match files bigger than specified size. Valid format examples: 1g, 4Gb, 1.5MB

    :returns:
        - ``{filesize}`` -- File size in bytes

    Examples:
        - Trash big downloads:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Downloads'
                filters:
                  - FileSize:
                      - smaller: 5g
                      - bigger: 1m
                actions:
                  - Trash

    """

    @staticmethod
    def _parse_size_arg(size_string):
        size_number, size_unit = re.findall(r'([0-9\.]+)\s*([A-Za-z]+)', size_string)[0]
        unit_lookup = {
            'k': 3,
            'm': 6,
            'g': 9,
            't': 12,
            'p': 15,
        }
        return float(size_number) * pow(10, unit_lookup[size_unit.strip().lower()[0]])

    def __init__(self, smaller=None, bigger=None):
        if smaller is not None:
            smaller = self._parse_size_arg(smaller)
        if bigger is not None:
            bigger = self._parse_size_arg(bigger)

        self.smaller=smaller
        self.bigger=bigger

    def matches(self, path):
        file_size = self._get_file_size(path)
        return (self.smaller is None or (file_size <= self.smaller)) and \
               (self.bigger is None or (file_size >= self.bigger))

    def parse(self, path):
        file_size = self._get_file_size(path)
        return {'filesize': file_size}

    def _get_file_size(self, path):
        return os.path.getsize(path)

    def __str__(self):
        return 'FileSize(file_size=%d, mode=%s)' % (
            self.file_size, self.mode)
