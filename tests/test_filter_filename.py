from organize.utils import Path
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
