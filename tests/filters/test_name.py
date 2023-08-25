import fs

from organize.filters import Name


def test_name_startswith():
    name = Name(startswith="begin")
    assert name.matches("beginhere")
    assert not name.matches(".beginhere")
    assert not name.matches("herebegin")


def test_name_contains():
    name = Name(contains="begin")
    assert name.matches("beginhere")
    assert name.matches(".beginhere")
    assert name.matches("herebegin")
    assert not name.matches("other")


def test_name_endswith():
    name = Name(endswith="end")
    assert name.matches("hereend")
    assert name.matches("end")
    assert not name.matches("theendishere")


def test_name_multiple():
    name = Name(startswith="begin", contains="con", endswith="end")
    assert name.matches("begin_somethgin_con_end")
    assert not name.matches("beginend")
    assert not name.matches("begincon")
    assert not name.matches("conend")
    assert name.matches("beginconend")


def test_name_case():
    name = Name(startswith="star", contains="con", endswith="end", case_sensitive=False)
    assert name.matches("STAR_conEnD")
    assert not name.matches("STAREND")
    assert not name.matches("STARCON")
    assert not name.matches("CONEND")
    assert name.matches("STARCONEND")


def test_name_list():
    name = Name(
        startswith="_",
        contains=["1", "A", "3", "6"],
        endswith=["5", "6"],
        case_sensitive=False,
    )
    assert name.matches("_15")
    assert name.matches("_A5")
    assert name.matches("_A6")
    assert name.matches("_a6")
    assert name.matches("_35")
    assert name.matches("_36")
    assert name.matches("_somethinga56")
    assert name.matches("_6")
    assert not name.matches("")
    assert not name.matches("a_5")


def test_name_list_case_sensitive():
    name = Name(
        startswith="_",
        contains=["1", "A", "3", "7"],
        endswith=["5", "6"],
        case_sensitive=True,
    )
    assert name.matches("_15")
    assert name.matches("_A5")
    assert name.matches("_A6")
    assert not name.matches("_a6")
    assert name.matches("_35")
    assert name.matches("_36")
    assert name.matches("_somethingA56")
    assert not name.matches("_6")
    assert not name.matches("_a5")
    assert not name.matches("-A5")
    assert not name.matches("")
    assert not name.matches("_a5")


def test_name_match():
    with fs.open_fs("mem://") as mem:
        p = "Invoice_RE1001_2021_01_31"
        fs_path = p + ".txt"
        mem.touch(fs_path)
        fn = Name("Invoice_*_{year:int}_{month}_{day}")
        assert fn.matches(p)
        result = fn.run(fs=mem, fs_path=fs_path)
        assert result.matches
        assert result.updates == {"name": {"year": 2021, "month": "01", "day": "31"}}


def test_name_match_case_insensitive():
    with fs.open_fs("mem://") as mem:
        p = "UPPER_MiXed_lower"
        fs_path = p + ".txt"
        mem.touch(fs_path)
        case = Name("upper_{m1}_{m2}", case_sensitive=True)
        icase = Name("upper_{m1}_{m2}", case_sensitive=False)
        assert icase.matches(p)
        result = icase.run(fs=mem, fs_path=fs_path)
        assert result.matches
        assert result.updates == {"name": {"m1": "MiXed", "m2": "lower"}}
        assert not case.matches(p)
