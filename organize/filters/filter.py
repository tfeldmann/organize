from textwrap import indent
from typing import Any, Callable, Dict, Optional, Union

from colorama import Fore, Style  # type: ignore

from organize.utils import DotDict

FilterResult = Union[Dict[str, Any], bool, None]


class Filter:
    pre_print_hook = None  # type: Optional[Callable]

    def run(self, **kwargs: Dict) -> FilterResult:
        return self.pipeline(DotDict(kwargs))

    def pipeline(self, args: DotDict) -> FilterResult:
        raise NotImplementedError

    def print(self, msg: str) -> None:
        """ print a message for the user """
        if callable(self.pre_print_hook):
            self.pre_print_hook()  # pylint: disable=not-callable
        print(indent("- (%s) %s" % (self.__class__.__name__, msg), " " * 4))

    def print_exception(self, exc: Exception) -> None:
        self.print(Fore.RED + Style.BRIGHT + "ERROR! %s" % exc)

    def __str__(self) -> str:
        """ Return filter name and properties """
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
