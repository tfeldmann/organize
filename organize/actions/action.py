from typing import Optional
from clint.textui import puts
from organize.utils import Path


class Error(Exception):
    pass


class TemplateAttributeError(Error):
    pass


class Action:

    def run(self, attrs: dict, simulate: bool) -> Optional[Path]:
        # if you change the file path, return the new path here
        raise NotImplementedError

    def print(self, msg):
        """ print a message for the user """
        puts('- [%s] %s' % (self.__class__.__name__, msg))

    @staticmethod
    def fill_template_tags(msg: str, attrs: dict) -> str:
        try:
            return msg.format(**attrs)
        except AttributeError as exc:
            cause = exc.args[0]
            raise TemplateAttributeError(
                'Missing template variable %s for "%s"' % (cause, msg))

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % str(self)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.__dict__ == other.__dict__)
