from clint.textui import puts
from organize.utils import Path


class Error(Exception):
    pass


class TemplateAttributeError(Error):
    pass


class Action:

    def run(self, path, attrs, simulate):
        # type: (Path, dict, bool) -> None
        # if you change the file path, return the new path here
        raise NotImplementedError

    def print(self, msg):
        # print a message for the user
        puts('- %s: %s' % (self.__class__.__name__, msg))

    def fill_template_tags(self, msg, path, attrs):
        try:
            return msg.format(path=path, **attrs)
        except AttributeError as e:
            cause = e.args[0]
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
