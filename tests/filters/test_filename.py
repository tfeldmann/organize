from organize.compat import Path
from organize.filters import Filename


def test_filename_startswith():
    filename = Filename(startswith="begin")
    assert filename.run(Path("~/here/beginhere.pdf"))
    assert not filename.run(Path("~/here/.beginhere.pdf"))
    assert not filename.run(Path("~/here/herebegin.begin"))


def test_filename_contains():
    filename = Filename(contains="begin")
    assert filename.run(Path("~/here/beginhere.pdf"))
    assert filename.run(Path("~/here/.beginhere.pdf"))
    assert filename.run(Path("~/here/herebegin.begin"))
    assert not filename.run(Path("~/here/other.begin"))


def test_filename_endswith():
    filename = Filename(endswith="end")
    assert filename.run(Path("~/here/hereend.pdf"))
    assert not filename.run(Path("~/here/end.tar.gz"))
    assert not filename.run(Path("~/here/theendishere.txt"))


def test_filename_multiple():
    filename = Filename(startswith="begin", contains="con", endswith="end")
    assert filename.run(Path("~/here/begin_somethgin_con_end.pdf"))
    assert not filename.run(Path("~/here/beginend.pdf"))
    assert not filename.run(Path("~/here/begincon.begin"))
    assert not filename.run(Path("~/here/conend.begin"))
    assert filename.run(Path("~/here/beginconend.begin"))


def test_filename_case():
    filename = Filename(
        startswith="star", contains="con", endswith="end", case_sensitive=False
    )
    assert filename.run(Path("~/STAR_conEnD.dpf"))
    assert not filename.run(Path("~/here/STAREND.pdf"))
    assert not filename.run(Path("~/here/STARCON.begin"))
    assert not filename.run(Path("~/here/CONEND.begin"))
    assert filename.run(Path("~/here/STARCONEND.begin"))


def test_filename_list():
    filename = Filename(
        startswith="_",
        contains=["1", "A", "3", "6"],
        endswith=["5", "6"],
        case_sensitive=False,
    )
    assert filename.run(Path("~/_15.dpf"))
    assert filename.run(Path("~/_A5.dpf"))
    assert filename.run(Path("~/_A6.dpf"))
    assert filename.run(Path("~/_a6.dpf"))
    assert filename.run(Path("~/_35.dpf"))
    assert filename.run(Path("~/_36.dpf"))
    assert filename.run(Path("~/_somethinga56"))
    assert filename.run(Path("~/_6"))
    assert not filename.run(Path("~/"))
    assert not filename.run(Path("~/a_5"))


def test_filename_list_case_sensitive():
    filename = Filename(
        startswith="_",
        contains=["1", "A", "3", "7"],
        endswith=["5", "6"],
        case_sensitive=True,
    )
    assert filename.run(Path("~/_15.dpf"))
    assert filename.run(Path("~/_A5.dpf"))
    assert filename.run(Path("~/_A6.dpf"))
    assert not filename.run(Path("~/_a6.dpf"))
    assert filename.run(Path("~/_35.dpf"))
    assert filename.run(Path("~/_36.dpf"))
    assert filename.run(Path("~/_somethingA56"))
    assert not filename.run(Path("~/_6"))
    assert not filename.run(Path("~/_a5.dpf"))
    assert not filename.run(Path("~/-A5.dpf"))
    assert not filename.run(Path("~/"))
    assert not filename.run(Path("~/_a5"))
