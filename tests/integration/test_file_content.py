from conftest import create_filesystem, assertdir
from organize.cli import main


def test_file_content(tmp_path):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    create_filesystem(
        tmp_path,
        files=[
            ("Test1.txt", "Invoice 12345"),
            ("Test2.txt", "Tests"),
            ("Test3.txt", "My Homework ...")
        ],
        config=r"""
        rules:
        - folders: files
          filters:
            - filecontent: '.*Invoice (?P<number>\w+).*'
          actions:
            - rename: "Invoice_{filecontent.number}.txt"
        - folders: files
          filters:
            - filecontent: '.*Homework.*'
          actions:
            - rename: "Homework.txt"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "Homework.txt", "Invoice_12345.txt", "Test2.txt")
