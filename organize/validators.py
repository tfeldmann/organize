from typing import Annotated, Any, Iterable, List, Mapping, TypeVar

from pydantic.functional_validators import BeforeValidator


def islist(x):
    return isinstance(x, Iterable) and not isinstance(x, (str, bytes, Mapping))


def _flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if islist(x):
            yield from _flatten(x)
        else:
            yield x


def flatten(x: Any):
    if x is None:
        return []
    if not islist(x):
        x = (x,)
    return list(_flatten(x))


T = TypeVar("T")
FlatList = Annotated[List[T], BeforeValidator(flatten)]
FlatSet = Annotated[List[T], BeforeValidator(flatten)]
