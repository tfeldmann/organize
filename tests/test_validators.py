from pydantic.type_adapter import TypeAdapter

from organize.validators import FlatList


def test_flatlist():
    ta = TypeAdapter(FlatList[int])
    v = ta.validate_python([1, 2, [10, 11, [12, 23]], 3, [4, 5, 6]])
    assert v == [1, 2, 10, 11, 12, 23, 3, 4, 5, 6]
    assert ta.validate_python(None) == []
