import sys

import pytest

from organize import Config
from organize.filters.macos_tags import list_tags, matches_tags


def test_macos_tags_matching():
    filter_tags = ("Invoice (*)", "* (red)", "Test (green)")
    assert matches_tags(filter_tags=filter_tags, file_tags=["Invoice (none)"])
    assert matches_tags(filter_tags=filter_tags, file_tags=["Invoice (green)"])
    assert not matches_tags(filter_tags=filter_tags, file_tags=["Voice (green)"])
    assert matches_tags(filter_tags=filter_tags, file_tags=["Voice (red)"])
    assert not matches_tags(filter_tags=filter_tags, file_tags=["Test (blue)"])
    assert matches_tags(filter_tags=filter_tags, file_tags=["Test (green)"])
    assert matches_tags(filter_tags=["Invoice (red)"], file_tags=["Invoice (red)"])
    assert matches_tags(
        filter_tags=("Invoice (red)", "* (green)"),
        file_tags=["Invoice (red)"],
    )

    assert matches_tags(["Invoice (red)", "* (green)"], ["Urgent (green)"])
    assert matches_tags(["Invoice (red)", "* (green)"], ["Invoice (red)"])
    assert not matches_tags(["Invoice (red)", "* (green)"], ["Pictures (blue)"])


@pytest.mark.skipif(sys.platform != "darwin", reason="runs only on macOS")
def test_macos_filter(tmp_path, testoutput):
    import macos_tags

    testdir = tmp_path / "test"
    testdir.mkdir()

    invoice = testdir / "My-Invoice.pdf"
    invoice.touch()
    macos_tags.add(macos_tags.Tag("Invoice", macos_tags.Color.RED), file=invoice)
    assert list_tags(invoice) == ["Invoice (red)"]

    another = testdir / "Another-File.pdf"
    another.touch()
    macos_tags.add(macos_tags.Tag("Urgent", macos_tags.Color.GREEN), file=another)
    assert list_tags(another) == ["Urgent (green)"]

    pic = testdir / "Pic.jpg"
    pic.touch()
    macos_tags.add(macos_tags.Tag("Pictures", macos_tags.Color.BLUE), file=pic)
    assert list_tags(pic) == ["Pictures (blue)"]

    Config.from_string(
        f"""
        rules:
          - locations: {testdir}
            filters:
            - macos_tags:
                - "Invoice (red)"
                - "* (green)"
            actions:
            - echo: "{{','.join(macos_tags)}}"
        """
    ).execute(simulate=False, output=testoutput)

    assert set(testoutput.messages) == set(["Invoice (red)", "Urgent (green)"])
