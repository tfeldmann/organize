from textwrap import indent
from typing import Any, Mapping, Optional, Callable

from organize.utils import DotDict


class Error(Exception):
    pass


class TemplateAttributeError(Error):
    pass


class Action:
    pre_print_hook = None  # type: Optional[Callable]

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def schema(cls):
        from schema import Schema, Optional, Or

        return {
            Optional(cls.name().lower()): Or(
                str,
                [str],
                Schema({}, ignore_extra_keys=True),
            ),
        }

    def run(self, **kwargs) -> Optional[Mapping[str, Any]]:
        return self.pipeline(DotDict(kwargs))

    def pipeline(self, args: DotDict) -> Optional[Mapping[str, Any]]:
        raise NotImplementedError

    def print(self, msg) -> None:
        """print a message for the user"""
        if callable(self.pre_print_hook):
            self.pre_print_hook(name=self.name(), msg=msg)

    @staticmethod
    def fill_template_tags(msg: str, args) -> str:
        try:
            return msg.format(**args)
        except AttributeError as exc:
            cause = exc.args[0]
            raise TemplateAttributeError(
                'Missing template variable %s for "%s"' % (cause, msg)
            )

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
