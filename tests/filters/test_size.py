import pytest
from conftest import make_files, read_files

from organize import core
from organize.filters import Size


def test_constrains_mope1():
    assert not Size("<1b,>2b").matches(1)
    assert Size(">=1b,<2b").matches(1)
    assert not Size(">1.000001b").matches(1)
    assert Size("<1.000001B").matches(1)
    assert Size("<1.000001").matches(1)
    assert Size("<=1,>=0.001kb").matches(1)
    assert Size("<1").matches(0)
    assert not Size(">1").matches(0)
    assert not Size("<1,>1b").matches(0)
    assert Size(">99.99999GB").matches(100000000000)
    assert Size("0").matches(0)


def test_constrains_base():
    assert Size(">1kb,<1kib").matches(1010)
    assert Size(">1k,<1ki").matches(1010)
    assert Size("1k").matches(1000)
    assert Size("1000").matches(1000)


def test_other():
    assert Size("<100 Mb").matches(20)
    assert Size("<100 Mb, <10 mb, <1 mb, > 0").matches(20)
    assert Size(["<100 Mb", ">= 0 Tb"]).matches(20)


def test_size_zero(testfs):
    files = {"1": "", "2": "", "3": ""}
    make_files(testfs, files)
    config = """
        rules:
        - locations: "."
          filters:
            - size: 0
          actions:
            - echo: '{path.name}'
            - delete
        """
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {}


def test_basic(testfs):
    files = {
        "empty": "",
        "full": "0" * 2000,
        "halffull": "0" * 1010,
        "two_thirds.txt": "0" * 666,
    }
    make_files(testfs, files)
    config = """
        rules:
        - locations: "."
          filters:
            - size: '> 1kb, <= 1.0 KiB'
          actions:
            - echo: '{path.name} {size.bytes}'
        - locations: "."
          filters:
            - not size:
              - '> 0.5 kb'
              - '<1.0 KiB'
          actions:
            - delete
        """
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "halffull": "0" * 1010,
        "two_thirds.txt": "0" * 666,
    }


# @pytest.mark.skip(reason="TODO - template vars in filters not supported")
# def test_python_args(tmp_path, mock_echo):
#     create_filesystem(
#         tmp_path,
#         files=[
#             "empty",
#             ("full", "0" * 2000),
#             ("halffull", "0" * 1010),
#             ("two_thirds.txt", "0" * 666),
#         ],
#         config="""
#         rules:
#         - folders: files
#           filters:
#             - python: |
#                 return 2000
#             - filesize: '= {python}b'
#           actions:
#             - echo: '{path.name} {filesize.bytes}'
#         """,
#     )
#     main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
#     mock_echo.assert_has_calls(
#         [
#             call("full 2000"),
#         ],
#         any_order=True,
#     )
