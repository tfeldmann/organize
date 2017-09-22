import re


class Regex:

    """ Matches filenames with the given regular expression
    """

    def __init__(self, expr):
        self.expr = re.compile(expr)

    def matches(self, path):
        return self.expr.match(path.name)

    def parse(self, path):
        return {}

    def __str__(self):
        return 'Regex'

    def __repr__(self):
        return '<Regex>'
