from conftest import make_files, read_files

from organize import Config, app_support, history


def test_info(tmp_path):
    (tmp_path / "in").mkdir()
    config = Config.from_string(
        f"""
        rules:
          - locations: '{tmp_path}/in'
            filters:
              - ai:
                  categories: [invoice, tax]
                  uncertain: Check
            actions:
              - echo: "x"
          - locations: '{tmp_path}/in'
            filters:
              - ai:
                  categories: [tax, photos]
            actions:
              - echo: "x"
        """
    )
    result = app_support.info(config)
    assert result["folders"] == [str((tmp_path / "in").resolve())]
    assert result["categories"] == ["invoice", "tax", "photos"]
    assert result["review_folders"] == ["Check", "_Review"]


def test_move_is_undoable(fs):
    make_files({"_Review": {"a.pdf": "new"}, "tax": {"a.pdf": "old"}}, "dl")
    dst = app_support.move(
        app_support.Path("/dl/_Review/a.pdf"), app_support.Path("/dl/tax")
    )
    assert (dst.parent.name, dst.name) == ("tax", "a 2.pdf")
    assert read_files("dl") == {
        "_Review": {},
        "tax": {"a.pdf": "old", "a 2.pdf": "new"},
    }

    run = history.last_run()
    assert run is not None
    list(history.undo(run, simulate=False))
    assert read_files("dl") == {"_Review": {"a.pdf": "new"}, "tax": {"a.pdf": "old"}}


def test_move_creates_folder(fs):
    make_files({"a.pdf": "x"}, "dl")
    app_support.move(app_support.Path("/dl/a.pdf"), app_support.Path("/dl/invoice"))
    assert read_files("dl") == {"invoice": {"a.pdf": "x"}}
    run = history.last_run()
    assert run is not None
    list(history.undo(run, simulate=False))
    assert read_files("dl") == {"a.pdf": "x"}
