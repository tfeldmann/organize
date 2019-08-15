from organize.utils import (
    DotDict,
    Path,
    dict_merge,
    find_unused_filename,
    increment_filename_version,
    splitglob,
)


def test_splitglob():
    assert splitglob("~/Downloads") == (Path.home() / "Downloads", "")
    assert splitglob(r"/Test/\* tmp\*/*[!H]/**/*.*") == (
        Path(r"/Test/\* tmp\*"),
        "*[!H]/**/*.*",
    )
    assert splitglob("~/Downloads/Program 0.1*.exe") == (
        Path.home() / "Downloads",
        "Program 0.1*.exe",
    )
    assert splitglob("~/Downloads/Program[ms].exe") == (
        Path.home() / "Downloads",
        "Program[ms].exe",
    )
    assert splitglob("~/Downloads/Program.exe") == (
        Path.home() / "Downloads" / "Program.exe",
        "",
    )
    # https://github.com/tfeldmann/organize/issues/40
    assert splitglob("~/Ältere/Erträgnisaufstellung_*.pdf") == (
        Path.home() / "Ältere",
        "Erträgnisaufstellung_*.pdf",
    )
    # https://github.com/tfeldmann/organize/issues/39
    assert splitglob("~/Downloads/*.pdf") == (Path.home() / "Downloads", "*.pdf")


def test_unused_filename_basic(mock_exists):
    mock_exists.return_value = False
    assert find_unused_filename(Path("somefile.jpg")) == Path("somefile 2.jpg")


def test_unused_filename_separator(mock_exists):
    mock_exists.return_value = False
    assert find_unused_filename(Path("somefile.jpg"), separator="_") == Path(
        "somefile_2.jpg"
    )


def test_unused_filename_multiple(mock_exists):
    mock_exists.side_effect = [True, True, False]
    assert find_unused_filename(Path("somefile.jpg")) == Path("somefile 4.jpg")


def test_unused_filename_increase(mock_exists):
    mock_exists.side_effect = [True, False]
    assert find_unused_filename(Path("somefile 7.jpg")) == Path("somefile 9.jpg")


def test_unused_filename_increase_digit(mock_exists):
    mock_exists.side_effect = [True, False]
    assert find_unused_filename(Path("7.gif")) == Path("7 3.gif")


def test_increment_filename_version():
    assert (
        increment_filename_version(Path.home() / "f3" / "test_123.7z")
        == Path.home() / "f3" / "test_123 2.7z"
    )
    assert (
        increment_filename_version(Path.home() / "f3" / "test_123_2 10.7z")
        == Path.home() / "f3" / "test_123_2 11.7z"
    )


def test_increment_filename_version_separator():
    assert increment_filename_version(Path("test_123.7z"), separator="_") == Path(
        "test_124.7z"
    )
    assert increment_filename_version(Path("test_123_2.7z"), separator="_") == Path(
        "test_123_3.7z"
    )


def test_increment_filename_version_no_separator():
    assert increment_filename_version(Path("test.7z"), separator="") == Path("test2.7z")
    assert increment_filename_version(Path("test 10.7z"), separator="") == Path(
        "test 102.7z"
    )


def test_merges_dicts():
    a = {"a": 1, "b": {"b1": 2, "b2": 3}}
    b = {"a": 1, "b": {"b1": 4}}

    assert dict_merge(a, b)["a"] == 1
    assert dict_merge(a, b)["b"]["b2"] == 3
    assert dict_merge(a, b)["b"]["b1"] == 4


def test_returns_copy():
    a = {"regex": {"first": "A", "second": "B"}}
    b = {"regex": {"third": "C"}}

    x = dict_merge(a, b)
    a["regex"]["first"] = "X"
    assert x["regex"]["first"] == "A"
    assert x["regex"]["second"] == "B"
    assert x["regex"]["third"] == "C"


def test_inserts_new_keys():
    """Will it insert new keys by default?"""
    a = {"a": 1, "b": {"b1": 2, "b2": 3}}
    b = {"a": 1, "b": {"b1": 4, "b3": 5}, "c": 6}

    assert dict_merge(a, b)["a"] == 1
    assert dict_merge(a, b)["b"]["b2"] == 3
    assert dict_merge(a, b)["b"]["b1"] == 4
    assert dict_merge(a, b)["b"]["b3"] == 5
    assert dict_merge(a, b)["c"] == 6


def test_does_not_insert_new_keys():
    """Will it avoid inserting new keys when required?"""
    a = {"a": 1, "b": {"b1": 2, "b2": 3}}
    b = {"a": 1, "b": {"b1": 4, "b3": 5}, "c": 6}

    assert dict_merge(a, b, add_keys=False)["a"] == 1
    assert dict_merge(a, b, add_keys=False)["b"]["b2"] == 3
    assert dict_merge(a, b, add_keys=False)["b"]["b1"] == 4
    try:
        assert dict_merge(a, b, add_keys=False)["b"]["b3"] == 5
    except KeyError:
        pass
    else:
        raise Exception("New keys added when they should not be")

    try:
        assert dict_merge(a, b, add_keys=False)["b"]["b3"] == 6
    except KeyError:
        pass
    else:
        raise Exception("New keys added when they should not be")


def test_dotdict_merge():
    a = DotDict()
    b = {1: {2: 2, 3: 3, 4: {5: "fin."}}}
    a.update(b)
    assert a == b
    b[1][2] = 5
    assert a != b

    a.update({1: {4: {5: "new.", 6: "fin."}, 2: "x"}})
    assert a == {1: {2: "x", 3: 3, 4: {5: "new.", 6: "fin."}}}


def test_dotdict_keeptype():
    a = DotDict()
    a.update({"nr": {"upper": 1}})
    assert a.nr.upper == 1

    assert "{nr.upper}".format(**a) == "1"
