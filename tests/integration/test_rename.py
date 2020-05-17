from conftest import create_filesystem, assertdir
from organize.cli import main


def test_rename_issue51(tmp_path):
    # test for issue https://github.com/tfeldmann/organize/issues/51
    create_filesystem(
        tmp_path,
        files=["19asd_WF_test2.pdf", "other.pdf", "18asd_WFX_test2.pdf",],
        config=r"""
        rules:
            - folders: files
              filters:
                - filename:
                    startswith: "19"
                    contains:
                      - "_WF_"
              actions:
                - rename: "{path.stem}_unread{path.suffix}"
                - copy:
                    dest: "files/copy/"
                    overwrite: false
                    counter_separator: "_"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "19asd_WF_test2_unread.pdf",
        "other.pdf",
        "copy/19asd_WF_test2_unread.pdf",
        "18asd_WFX_test2.pdf",
    )
