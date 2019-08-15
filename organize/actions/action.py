from textwrap import indent
from typing import Optional

from organize.utils import DotDict


class Error(Exception):
    pass


class TemplateAttributeError(Error):
    pass


class Action:
    def run(self, **kwargs):
        return self.pipeline(DotDict(kwargs))

    def pipeline(self, args: DotDict) -> Optional[dict]:
        raise NotImplementedError

    def print(self, msg):
        """ print a message for the user """
        print(indent("- [%s] %s" % (self.__class__.__name__, msg), " " * 4))

    @staticmethod
    def fill_template_tags(msg: str, args) -> str:
        try:
            return msg.format(**args)
        except AttributeError as exc:
            cause = exc.args[0]
            raise TemplateAttributeError(
                'Missing template variable %s for "%s"' % (cause, msg)
            )

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return "<%s>" % str(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
