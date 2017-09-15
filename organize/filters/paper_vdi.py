import re

expr = re.compile(r'^VDInachrichten-(\d{4})(\d{2})(\d{2})\.pdf$')


class PaperVDI:

    def matches(self, path):
        return expr.match(path.name) is not None

    def parse(self, path):
        year, month, day = expr.match(path.name).groups()
        return {
            'year': int(year),
            'month': int(month),
            'day': int(day)
        }
