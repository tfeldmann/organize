import sys

import pytest

from organize import Config, duplicates

MARK_AND_SORT = """
rules:
  - locations: "{loc}"
    subfolders: false
    filters:
      - copy_of
    actions:
      - mark_duplicate
  - locations: "{loc}"
    subfolders: false
    filters:
      - extension
    actions:
      - move: "{loc}/sorted/"
"""


def run(loc, search=""):
    Config.from_string(MARK_AND_SORT.replace("{loc}", str(loc))).execute(simulate=False)


def make(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_copy_of_sorted_file_is_marked_and_still_sorted(tmp_path):
    original = make(tmp_path / "invoice" / "Telekom" / "bill.pdf", "same content")
    make(tmp_path / "Rechnung (1).pdf", "same content")
    make(tmp_path / "other.pdf", "different")
    run(tmp_path)

    copy = tmp_path / "sorted" / "Rechnung (1).pdf"
    assert copy.exists()
    assert duplicates.original_of(copy) == original.resolve()
    assert duplicates.original_of(tmp_path / "sorted" / "other.pdf") is None
    assert duplicates.original_of(original) is None


@pytest.mark.skipif(sys.platform != "darwin", reason="Finder tags")
def test_finder_tag(tmp_path):
    import macos_tags

    make(tmp_path / "keep" / "a.txt", "x")
    make(tmp_path / "b.txt", "x")
    run(tmp_path)
    tags = [t.name for t in macos_tags.get_all(str(tmp_path / "sorted" / "b.txt"))]
    assert tags == ["Duplicate"]

    duplicates.unmark(tmp_path / "sorted" / "b.txt")
    assert macos_tags.get_all(str(tmp_path / "sorted" / "b.txt")) == []
    assert duplicates.original_of(tmp_path / "sorted" / "b.txt") is None


def test_first_of_new_copies_is_the_original(tmp_path):
    make(tmp_path / "a.txt", "twin")
    make(tmp_path / "b.txt", "twin")
    run(tmp_path)
    marked = duplicates.find_marked([tmp_path])
    assert len(marked) == 1
    assert marked[0]["path"].endswith("sorted/b.txt")
    # the original was sorted after b.txt was marked and is found by its content
    assert marked[0]["original"].endswith("sorted/a.txt")
    assert marked[0]["original_exists"] is True


def test_same_size_different_content_and_empty_files(tmp_path):
    make(tmp_path / "old" / "a.txt", "aaaa")
    make(tmp_path / "b.txt", "bbbb")
    make(tmp_path / "old" / "empty.txt", "")
    make(tmp_path / "empty2.txt", "")
    run(tmp_path)
    assert duplicates.find_marked([tmp_path]) == []


def test_search_other_folders(tmp_path):
    make(tmp_path / "Documents" / "contract.pdf", "signed")
    make(tmp_path / "Downloads" / "contract-copy.pdf", "signed")
    Config.from_string(
        f"""
        rules:
          - locations: "{tmp_path}/Downloads"
            filters:
              - copy_of:
                  search: "{tmp_path}/Documents"
            actions:
              - mark_duplicate
        """
    ).execute(simulate=False)
    marked = duplicates.find_marked([tmp_path / "Downloads"])
    assert [m["original"] for m in marked] == [
        str((tmp_path / "Documents" / "contract.pdf").resolve())
    ]


def test_simulation_marks_nothing(tmp_path):
    make(tmp_path / "keep" / "a.txt", "x")
    make(tmp_path / "b.txt", "x")
    Config.from_string(MARK_AND_SORT.replace("{loc}", str(tmp_path))).execute(
        simulate=True
    )
    assert duplicates.find_marked([tmp_path]) == []


def test_third_copy_points_to_the_original(tmp_path):
    original = make(tmp_path / "keep" / "a.txt", "x")
    make(tmp_path / "b.txt", "x")
    run(tmp_path)
    make(tmp_path / "c.txt", "x")
    run(tmp_path)
    marked = {m["path"]: m["original"] for m in duplicates.find_marked([tmp_path])}
    assert marked == {
        str(tmp_path / "sorted" / "b.txt"): str(original.resolve()),
        str(tmp_path / "sorted" / "c.txt"): str(original.resolve()),
    }


def test_find_existing_keeps_the_oldest(tmp_path):
    import os

    old = make(tmp_path / "invoice" / "bill.pdf", "same")
    new = make(tmp_path / "Documents" / "bill (1).pdf", "same")
    make(tmp_path / "Documents" / "other.pdf", "else")
    os.utime(old, (1_000_000, 1_000_000))
    found = duplicates.find_existing([old, new, tmp_path / "Documents" / "other.pdf"])
    assert found == [{"path": str(new), "original": str(old)}]


def test_sorted_files_leaves_out_moved_folders(tmp_path):
    make(tmp_path / "a.pdf", "A")
    make(tmp_path / "Project" / "LICENSE", "MIT")
    Config.from_string(
        f"""
        rules:
          - locations: "{tmp_path}"
            subfolders: false
            actions:
              - move: "{tmp_path}/docs/"
          - locations: "{tmp_path}"
            subfolders: false
            targets: dirs
            filters:
              - name: Project
            actions:
              - move: "{tmp_path}/projects/"
        """
    ).execute(simulate=False)
    assert duplicates.sorted_files([tmp_path]) == [tmp_path / "docs" / "a.pdf"]
