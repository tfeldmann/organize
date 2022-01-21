from schema import Schema, Optional, Or
from textwrap import indent
from typing import Any, Dict, Union

from organize.utils import DotDict

FilterResult = Union[Dict[str, Any], bool, None]


class Filter:
    pre_print_hook = None

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def schema(cls):
        return Or(
            cls.name(),
            {
                Optional(cls.name()): Or(
                    str,
                    [str],
                    Schema({}, ignore_extra_keys=True),
                ),
            },
        )

    def run(self, **kwargs: Dict) -> FilterResult:
        return self.pipeline(DotDict(kwargs))

    def pipeline(self, args: DotDict) -> FilterResult:
        raise NotImplementedError

    def print(self, msg: str) -> None:
        """print a message for the user"""
        if callable(self.pre_print_hook):
            self.pre_print_hook(name=self.name(), msg=msg)

    def __str__(self) -> str:
        """Return filter name and properties"""
        return self.name()

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
