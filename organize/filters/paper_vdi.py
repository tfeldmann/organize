import re
from organize.utils import DotDict
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
        year, month, day = expr.match(path.name).groups()
        result = DotDict({
            'year': int(year),
            'month': int(month),
            'day': int(day),
        })
        return {'vdi': result}
