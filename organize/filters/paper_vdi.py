import re
from collections import namedtuple
from .filter import Filter

expr = re.compile(r'^VDInachrichten-(\d{4})(\d{2})(\d{2})\.pdf$')


class PaperVDI(Filter):

    """
    Matches german VDI Nachrichten e-paper

    :returns:
        - `vdi.year` - the newspaper publication year
        - `vdi.month` - the newspaper publication month
        - `vdi.day` - the newspaper publication day
    """

    def matches(self, path):
        return expr.match(path.name) is not None

    def parse(self, path):
        Result = namedtuple('vdi', 'year month day')
        year, month, day = expr.match(path.name).groups()
        return {
            'vdi': Result(year=int(year), month=int(month), day=int(day))
        }
