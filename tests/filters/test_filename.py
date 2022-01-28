from organize.filters import Name


def test_filename_startswith():
    filename = Name(startswith="begin")
    assert filename.matches("~/here/beginhere.pdf")
    assert not filename.matches("~/here/.beginhere.pdf")
    assert not filename.matches("~/here/herebegin.begin")


def test_filename_contains():
    filename = Name(contains="begin")
    assert filename.matches("~/here/beginhere.pdf")
    assert filename.matches("~/here/.beginhere.pdf")
    assert filename.matches("~/here/herebegin.begin")
    assert not filename.matches("~/here/other.begin")


def test_filename_endswith():
    filename = Name(endswith="end")
    assert filename.matches("~/here/hereend.pdf")
    assert not filename.matches("~/here/end.tar.gz")
    assert not filename.matches("~/here/theendishere.txt")


def test_filename_multiple():
    filename = Name(startswith="begin", contains="con", endswith="end")
    assert filename.matches("~/here/begin_somethgin_con_end.pdf")
    assert not filename.matches("~/here/beginend.pdf")
    assert not filename.matches("~/here/begincon.begin")
    assert not filename.matches("~/here/conend.begin")
    assert filename.matches("~/here/beginconend.begin")


def test_filename_case():
    filename = Name(
        startswith="star", contains="con", endswith="end", case_sensitive=False
    )
    assert filename.matches("~/STAR_conEnD.dpf")
    assert not filename.matches("~/here/STAREND.pdf")
    assert not filename.matches("~/here/STARCON.begin")
    assert not filename.matches("~/here/CONEND.begin")
    assert filename.matches("~/here/STARCONEND.begin")


def test_filename_list():
    filename = Name(
        startswith="_",
        contains=["1", "A", "3", "6"],
        endswith=["5", "6"],
        case_sensitive=False,
    )
    assert filename.matches("~/_15.dpf")
    assert filename.matches("~/_A5.dpf")
    assert filename.matches("~/_A6.dpf")
    assert filename.matches("~/_a6.dpf")
    assert filename.matches("~/_35.dpf")
    assert filename.matches("~/_36.dpf")
    assert filename.matches("~/_somethinga56")
    assert filename.matches("~/_6")
    assert not filename.matches("~/")
    assert not filename.matches("~/a_5")


def test_filename_list_case_sensitive():
    filename = Name(
        startswith="_",
        contains=["1", "A", "3", "7"],
        endswith=["5", "6"],
        case_sensitive=True,
    )
    assert filename.matches("~/_15.dpf")
    assert filename.matches("~/_A5.dpf")
    assert filename.matches("~/_A6.dpf")
    assert not filename.matches("~/_a6.dpf")
    assert filename.matches("~/_35.dpf")
    assert filename.matches("~/_36.dpf")
    assert filename.matches("~/_somethingA56")
    assert not filename.matches("~/_6")
    assert not filename.matches("~/_a5.dpf")
    assert not filename.matches("~/-A5.dpf")
    assert not filename.matches("~/")
    assert not filename.matches("~/_a5")


def test_filename_match():
    fn = Name("Invoice_*_{year:int}_{month}_{day}")
    p = "~/Documents/Invoice_RE1001_2021_01_31.pdf"
    assert fn.matches(p)
    assert fn.run(p) == {"filename": {"year": 2021, "month": "01", "day": "31"}}


def test_filename_match_case_insensitive():
    case = Name("upper_{m1}_{m2}", case_sensitive=True)
    icase = Name("upper_{m1}_{m2}", case_sensitive=False)
    p = "~/Documents/UPPER_MiXed_lower.pdf"
    assert icase.matches(p)
    assert icase.run(path=p) == {"filename": {"m1": "MiXed", "m2": "lower"}}
    assert not case.matches(p)
