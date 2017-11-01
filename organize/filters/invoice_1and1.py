import re
import pathlib
from organize.utils import DotDict
from .filter import Filter

expr = re.compile(r'^RG(\d{12})\.pdf$')


class Invoice1and1(Filter):

    """
    Matches 1&1 invoice pdfs

    Always available:

    :returns:
        - `invoice_1and1.nr`    - the invoicing number

    The following data is only available if the pdf could be parsed:

    :returns:
        - `invoice_1and1.year`  - the invoice year
        - `invoice_1and1.month` - the invoice month
        - `invoice_1and1.day`   - the invoice day
        - `invoice_1and1.name`  - the name of the invoice recipient
    """

    def matches(self, path):
        return expr.match(path.name)

    def parse(self, path):
        result = DotDict()
        result['nr'] = expr.match(path.name).group(1)
        try:
            doc = self.parse_pdf(path)
            first_page = doc[0].split('\n')
            assert '1&1' in first_page[7]
            # parse name
            result['name'] = first_page[3]
            # parse date
            date = first_page[15]
            day, month, year = date.split('.')
            result['year'] = int(year)
            result['month'] = int(month)
            result['day'] = int(day)
        except Exception:
            pass
        return {'invoice_1and1': result}

    @staticmethod
    def parse_pdf(path: pathlib.Path):
        import slate3k
        with path.open('rb') as f:
            return slate3k.PDF(f)
