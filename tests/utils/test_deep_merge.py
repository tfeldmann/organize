from organize.utils import deep_merge, deep_merge_inplace


def test_merges_dicts():
    a = {"a": 1, "b": {"b1": 2, "b2": 3}}
    b = {"a": 1, "b": {"b1": 4}}

    print(deep_merge(a, b))
    assert deep_merge(a, b)["a"] == 1
    assert deep_merge(a, b)["b"]["b2"] == 3
    assert deep_merge(a, b)["b"]["b1"] == 4


def test_returns_copy():
    a = {"regex": {"first": "A", "second": "B"}}
    b = {"regex": {"third": "C"}}

    x = deep_merge(a, b)
    a["regex"]["first"] = "X"
    assert x["regex"]["first"] == "A"
    assert x["regex"]["second"] == "B"
    assert x["regex"]["third"] == "C"


def test_inserts_new_keys():
    """Will it insert new keys by default?"""
    a = {"a": 1, "b": {"b1": 2, "b2": 3}}
    b = {"a": 1, "b": {"b1": 4, "b3": 5}, "c": 6}

    assert deep_merge(a, b)["a"] == 1
    assert deep_merge(a, b)["b"]["b2"] == 3
    assert deep_merge(a, b)["b"]["b1"] == 4
    assert deep_merge(a, b)["b"]["b3"] == 5
    assert deep_merge(a, b)["c"] == 6


def test_does_not_insert_new_keys():
    """Will it avoid inserting new keys when required?"""
    a = {"a": 1, "b": {"b1": 2, "b2": 3}}
    b = {"a": 1, "b": {"b1": 4, "b3": 5}, "c": 6}

    assert deep_merge(a, b, add_keys=True) == {
        "a": 1,
        "b": {"b1": 4, "b2": 3, "b3": 5},
        "c": 6,
    }
    assert deep_merge(a, b, add_keys=False) == {
        "a": 1,
        "b": {"b1": 4, "b2": 3},
    }


def test_inplace_merge():
    a = {}
    b = {1: {2: 2, 3: 3, 4: {5: "fin."}}}
    a = deep_merge(a, b)
    assert a == b
    b[1][2] = 5
    assert a != b

    deep_merge_inplace(a, {1: {4: {5: "new.", 6: "fin."}, 2: "x"}})
    assert a == {1: {2: "x", 3: 3, 4: {5: "new.", 6: "fin."}}}


def test_inplace_keeptype():
    a = {}
    deep_merge_inplace(a, {"nr": {"upper": 1}})
    assert a["nr"]["upper"] == 1
