from conftest import create_filesystem, assertdir
from organize.cli import main


def test_globstr(tmp_path):
    # inspired by https://github.com/tfeldmann/organize/issues/39
    create_filesystem(
        tmp_path,
        files=[
            "Test.pdf",
            "Invoice.pdf",
            "Other.pdf",
            "Start.txt",
            "journal.md",
            "sub/test.pdf",
            "sub/other/marks.pdf",
        ],
        config="""
        rules:
        - folders: files/*.pdf
          actions:
            - shell: "rm {path}"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path, "Start.txt", "journal.md", "sub/test.pdf", "sub/other/marks.pdf"
    )


def test_globstr_subfolder(tmp_path):
    create_filesystem(
        tmp_path,
        files=[
            "Test.pdf",
            "Invoice.pdf",
            "Other.pdf",
            "Start.txt",
            "sub/journal.md",
            "sub/test.pdf",
            "sub/other/marks.pdf",
        ],
        config="""
        rules:
          - folders: files/**/*.pdf
            actions:
            - shell: "rm {path}"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "Start.txt", "sub/journal.md")


def test_globstr_subfolder_serious(tmp_path):
    create_filesystem(
        tmp_path,
        files=[
            "Test.pdf",
            "Invoice.pdf",
            "Other.pdf",
            "Start.txt",
            "x/foo/test.pdf",
            "x/sub/journal.md",
            "x/sub/journal.pdf",
            "wub/best.pdf",
            "sub/other/marks.pdf",
            "x/sub/testjournal.pdf",
            "sub/test.pdf",
            "wub/test.pdf",
            "dub/test.pdf",
        ],
        config="""
        rules:
            - folders:
              - files/**/*ub/**/test*.pdf
              - !files/dub/*
              actions:
              - shell: "rm {path}"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "Test.pdf",
        "Invoice.pdf",
        "Other.pdf",
        "Start.txt",
        "x/foo/test.pdf",
        "x/sub/journal.md",
        "x/sub/journal.pdf",
        "wub/best.pdf",
        "sub/other/marks.pdf",
        "dub/test.pdf",
    )


def test_globstr_exclude(tmp_path):
    create_filesystem(
        tmp_path,
        files=[
            "Test.pdf",
            "Invoice.pdf",
            "Start.txt",
            "other/a.txt",
            "other/next/b.txt",
            "exclude/test.pdf",
            "exclude/sub/journal.md",
            "exclude/sub/journal.pdf",
        ],
        config="""
        rules:
        - folders:
          - files/**/*
          - !files/exclude/*
          - '! files/*'
          actions:
          - shell: "rm {path}"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path, "Test.pdf", "Invoice.pdf", "Start.txt", "exclude/test.pdf",
    )


def test_globstr_subfolder_setting(tmp_path):
    create_filesystem(
        tmp_path,
        files=[
            "Test.pdf",
            "Invoice.pdf",
            "Other.pdf",
            "Start.txt",
            "sub/journal.md",
            "sub/test.pdf",
            "sub/other/marks.pdf",
        ],
        config="""
        rules:
            - folders: files
              subfolders: true
              filters:
              - extension: pdf
              actions:
              - shell: "rm {path}"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "Start.txt", "sub/journal.md")
