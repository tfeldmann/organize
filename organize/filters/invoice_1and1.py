import re
from . import helpers

expr = re.compile(r'^RG(\d{12})\.pdf$')


class Invoice1and1:

    """ Matches 1&1 pdf invoices

        Attributes:
            year, month, day    The invoice date
            name                The name the invoice is addressed to
            nr                  The invoice number
    """

    def matches(self, path):
        return expr.match(path.name)

    def parse(self, path):
        result = {}
        result['nr'] = expr.match(path.name).group(1)
        try:
            doc = helpers.parse_pdf(path)
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
        return result

    def __str__(self):
        return '1&1 Invoice'
