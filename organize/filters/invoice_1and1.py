import re
from . import helpers

expr = re.compile(r'^RG\d{12}\.pdf')


class Invoice1and1:

    def matches(self, path):
        return expr.match(path.name)

    def parse(self, path):
        result = {}
        doc = helpers.parse_pdf(path)
        import ipdb; ipdb.set_trace()
        return result
