from typing import Any, Iterable, List, TypeVar

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

T = TypeVar("T")


def _flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in _flatten(x):
                yield sub_x
        else:
            yield x


def ensure_flat(x: Any):
    return list(_flatten(x))


FlatList = Annotated[List[T], BeforeValidator(ensure_flat)]

if __name__ == "__main__":
    from pydantic.type_adapter import TypeAdapter

    ta = TypeAdapter(FlatList[int])
    v = ta.validate_python([1, 2, [10, 11, [12, 23]], 3, [4, 5, 6]])
    print(v)
