from pathlib import Path
from organize.filters import Filename


def test_filename_startswith():
    filename = Filename(startswith="begin")
    assert filename.matches(Path("~/here/beginhere.pdf"))
    assert not filename.matches(Path("~/here/.beginhere.pdf"))
    assert not filename.matches(Path("~/here/herebegin.begin"))


def test_filename_contains():
    filename = Filename(contains="begin")
    assert filename.matches(Path("~/here/beginhere.pdf"))
    assert filename.matches(Path("~/here/.beginhere.pdf"))
    assert filename.matches(Path("~/here/herebegin.begin"))
    assert not filename.matches(Path("~/here/other.begin"))


def test_filename_endswith():
    filename = Filename(endswith="end")
    assert filename.matches(Path("~/here/hereend.pdf"))
    assert not filename.matches(Path("~/here/end.tar.gz"))
    assert not filename.matches(Path("~/here/theendishere.txt"))


def test_filename_multiple():
    filename = Filename(startswith="begin", contains="con", endswith="end")
    assert filename.matches(Path("~/here/begin_somethgin_con_end.pdf"))
    assert not filename.matches(Path("~/here/beginend.pdf"))
    assert not filename.matches(Path("~/here/begincon.begin"))
    assert not filename.matches(Path("~/here/conend.begin"))
    assert filename.matches(Path("~/here/beginconend.begin"))


def test_filename_case():
    filename = Filename(
        startswith="star", contains="con", endswith="end", case_sensitive=False
    )
    assert filename.matches(Path("~/STAR_conEnD.dpf"))
    assert not filename.matches(Path("~/here/STAREND.pdf"))
    assert not filename.matches(Path("~/here/STARCON.begin"))
    assert not filename.matches(Path("~/here/CONEND.begin"))
    assert filename.matches(Path("~/here/STARCONEND.begin"))


def test_filename_list():
    filename = Filename(
        startswith="_",
        contains=["1", "A", "3", "6"],
        endswith=["5", "6"],
        case_sensitive=False,
    )
    assert filename.matches(Path("~/_15.dpf"))
    assert filename.matches(Path("~/_A5.dpf"))
    assert filename.matches(Path("~/_A6.dpf"))
    assert filename.matches(Path("~/_a6.dpf"))
    assert filename.matches(Path("~/_35.dpf"))
    assert filename.matches(Path("~/_36.dpf"))
    assert filename.matches(Path("~/_somethinga56"))
    assert filename.matches(Path("~/_6"))
    assert not filename.matches(Path("~/"))
    assert not filename.matches(Path("~/a_5"))


def test_filename_list_case_sensitive():
    filename = Filename(
        startswith="_",
        contains=["1", "A", "3", "7"],
        endswith=["5", "6"],
        case_sensitive=True,
    )
    assert filename.matches(Path("~/_15.dpf"))
    assert filename.matches(Path("~/_A5.dpf"))
    assert filename.matches(Path("~/_A6.dpf"))
    assert not filename.matches(Path("~/_a6.dpf"))
    assert filename.matches(Path("~/_35.dpf"))
    assert filename.matches(Path("~/_36.dpf"))
    assert filename.matches(Path("~/_somethingA56"))
    assert not filename.matches(Path("~/_6"))
    assert not filename.matches(Path("~/_a5.dpf"))
    assert not filename.matches(Path("~/-A5.dpf"))
    assert not filename.matches(Path("~/"))
    assert not filename.matches(Path("~/_a5"))


def test_filename_match():
    fn = Filename("Invoice_*_{year:int}_{month}_{day}")
    p = "~/Documents/Invoice_RE1001_2021_01_31.pdf"
    assert fn.matches(Path(p))
    assert fn.run(path=Path(p)) == {
        "filename": {"year": 2021, "month": "01", "day": "31"}
    }


def test_filename_match_case_insensitive():
    case = Filename("upper_{m1}_{m2}", case_sensitive=True)
    icase = Filename("upper_{m1}_{m2}", case_sensitive=False)
    p = "~/Documents/UPPER_MiXed_lower.pdf"
    assert icase.matches(Path(p))
    assert icase.run(path=Path(p)) == {"filename": {"m1": "MiXed", "m2": "lower"}}
    assert not case.matches(Path(p))
