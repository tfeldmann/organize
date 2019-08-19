from textwrap import indent
from typing import Optional

from organize.utils import DotDict


class Filter:
    pre_print_hook = None

    def run(self, **kwargs):
        return self.pipeline(DotDict(kwargs))

    def pipeline(self, args: DotDict) -> Optional[dict]:
        raise NotImplementedError

    def print(self, msg):
        """ print a message for the user """
        if callable(self.pre_print_hook):
            self.pre_print_hook()  # pylint: disable=not-callable
        print(indent("- (%s) %s" % (self.__class__.__name__, msg), " " * 4))

    def __str__(self):
        """ Return filter name and properties """
        return self.__class__.__name__

    def __repr__(self):
        return "<%s>" % str(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
