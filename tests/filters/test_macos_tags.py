import sys
import pytest
from fs import open_fs

from organize.filters import MacOSTags


@pytest.mark.skipif(sys.platform != "darwin", reason="runs only on macOS")
def test_macos_filter():
    import macos_tags

    tags = MacOSTags("Invoice (red)", "* (green)")
    with open_fs("temp://", writeable=True, create=True) as temp:
        temp.touch("My-Invoice.pdf")
        path = temp.getsyspath("My-Invoice.pdf")
        macos_tags.add(macos_tags.Tag("Invoice", macos_tags.Color.RED), file=path)

        temp.touch("Another-File.pdf")
        path = temp.getsyspath("Another-File.pdf")
        macos_tags.add(macos_tags.Tag("Urgent", macos_tags.Color.GREEN), file=path)

        temp.touch("Pic.jpg")
        path = temp.getsyspath("Pic.jpg")
        macos_tags.add(macos_tags.Tag("Pictures", macos_tags.Color.BLUE), file=path)

        assert tags.run(fs=temp, fs_path="My-Invoice.pdf").matches
        assert tags.run(fs=temp, fs_path="Another-File.pdf").matches
        assert not tags.run(fs=temp, fs_path="Pic.jpg").matches


def test_macos_tags_matching():
    tags = MacOSTags("Invoice (*)", "* (red)", "Test (green)")
    assert tags.matches(["Invoice (none)"])
    assert tags.matches(["Invoice (green)"])
    assert not tags.matches(["Voice (green)"])
    assert tags.matches(["Voice (red)"])
    assert not tags.matches(["Test (blue)"])
    assert tags.matches(["Test (green)"])
