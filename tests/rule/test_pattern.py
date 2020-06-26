from organize.rule import create_file_glob


def test_pattern():
    assert create_file_glob("~/Documents/*asd*/*asd.asd") == (
        "~/Documents",
        "*asd*/*asd.asd",
    )
    assert create_file_glob("~/Documents/*asd*/*asd.asd") == (
        "~/Documents",
        "*asd*/*asd.asd",
    )
    assert create_file_glob("~/Documents/**/*asd.asd/") == (
        "~/Documents",
        "**/*asd.asd",
    )
    assert create_file_glob("~/Tes*t/") == ("~", "Tes*t")
    assert create_file_glob(r"$USER_VAR/escaped\*char/main.*") == (
        r"$USER_VAR/escaped\*char",
        "main.*",
    )


def test_filesystem():
    assert create_file_glob("mem:///Pictures/cats/") == ("mem://Pictures/cats", "")
    assert create_file_glob("mem://Pics/**/DCF*.jpg") == ("mem://Pics", "**/DCF*.jpg")
