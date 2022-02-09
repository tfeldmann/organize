import os

from conftest import assertdir, create_filesystem

from organize.cli import main


def test_file_content(tmp_path):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    create_filesystem(
        tmp_path,
        files=[
            (
                "Test1.txt",
                "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
            ),
            ("Test2.txt", "Tests"),
            ("Test3.txt", "My Homework ..."),
        ],
        config=r"""
        rules:
        - folders: files
          filters:
            - filecontent: 'MegaCorp Ltd.+^Invoice (?P<number>\w+)$.+^ID: 98765$'
          actions:
            - rename: "MegaCorp_Invoice_{filecontent.number}.txt"
        - folders: files
          filters:
            - filecontent: '.*Homework.*'
          actions:
            - rename: "Homework.txt"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "Homework.txt", "MegaCorp_Invoice_12345.txt", "Test2.txt")
