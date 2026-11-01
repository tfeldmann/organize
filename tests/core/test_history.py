from conftest import make_files, read_files

from organize import Config, history

MOVE_AND_RENAME = """
rules:
  - locations: "/test"
    subfolders: false
    filters:
      - extension
    actions:
      - move: "/test/sorted/{extension}/"
      - rename: "renamed-{path.name}"
"""


def test_undo_restores_files_and_removes_new_folders(fs):
    make_files({"a.txt": "A", "b.pdf": "B", "keep": {"c.txt": "C"}}, "test")
    Config.from_string(MOVE_AND_RENAME).execute(simulate=False)
    assert read_files("test/sorted") == {
        "txt": {"renamed-a.txt": "A"},
        "pdf": {"renamed-b.pdf": "B"},
    }

    run = history.last_run()
    assert run is not None
    messages = list(history.undo(run, simulate=False))
    assert len(messages) == 7  # 2 renames, 2 moves, 3 new folders
    assert read_files("test") == {"a.txt": "A", "b.pdf": "B", "keep": {"c.txt": "C"}}


def test_dry_run_changes_nothing(fs):
    make_files({"a.txt": "A"}, "test")
    Config.from_string(MOVE_AND_RENAME).execute(simulate=False)
    run = history.last_run()
    assert run is not None
    messages = list(history.undo(run, simulate=True))
    assert any("Move back" in m for m in messages)
    assert read_files("test") == {"sorted": {"txt": {"renamed-a.txt": "A"}}}
    assert history.last_run() == run


def test_undo_goes_back_run_by_run(fs):
    make_files({"a.txt": "A"}, "test")
    Config.from_string(MOVE_AND_RENAME).execute(simulate=False)
    make_files({"b.txt": "B"}, "test")
    Config.from_string(MOVE_AND_RENAME).execute(simulate=False)
    first, second = history.runs()

    assert history.last_run() == second
    list(history.undo(second, simulate=False))
    assert history.last_run() == first
    list(history.undo(first, simulate=False))
    assert history.last_run() is None
    assert read_files("test") == {"a.txt": "A", "b.txt": "B"}


def test_simulation_is_not_recorded(fs):
    make_files({"a.txt": "A"}, "test")
    Config.from_string(MOVE_AND_RENAME).execute(simulate=True)
    assert history.runs() == []


def test_undo_skips_changed_files(fs):
    make_files({"a.txt": "A"}, "test")
    Config.from_string(MOVE_AND_RENAME).execute(simulate=False)
    make_files({"a.txt": "new file with the same name"}, "test")
    run = history.last_run()
    assert run is not None
    messages = list(history.undo(run, simulate=False))
    assert any("exists again" in m for m in messages)
    assert read_files("test/sorted/txt") == {"a.txt": "A"}


def test_undo_copy_trashes_the_copy(fs, monkeypatch):
    trashed = []
    monkeypatch.setattr(
        "organize.actions.trash.trash", lambda path: trashed.append(path)
    )
    make_files({"a.txt": "A"}, "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            subfolders: false
            actions:
              - copy: "/backup/"
        """
    ).execute(simulate=False)
    run = history.last_run()
    assert run is not None
    list(history.undo(run, simulate=False))
    assert [(p.parent.name, p.name) for p in trashed] == [("backup", "a.txt")]


def test_rename_existing_conflict_is_undone(fs):
    make_files({"a.txt": "new"}, "test")
    make_files({"a.txt": "existing"}, "target")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            actions:
              - move:
                  dest: "/target/"
                  on_conflict: rename_existing
        """
    ).execute(simulate=False)
    assert read_files("target") == {"a.txt": "new", "a 2.txt": "existing"}
    run = history.last_run()
    assert run is not None
    list(history.undo(run, simulate=False))
    assert read_files("target") == {"a.txt": "existing"}
    assert read_files("test") == {"a.txt": "new"}
