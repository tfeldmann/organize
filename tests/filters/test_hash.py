from pathlib import Path

from conftest import make_files

from organize import Config
from organize.filters.hash import hash, hash_first_chunk


def test_full_hash(fs):
    hello = Path("hello.txt")
    hello.write_text("Hello world\n")
    assert hash(hello, algo="md5") == "f0ef7081e1539ac00ef5b761b4fb01b3"
    assert hash(hello, algo="sha1") == "33ab5639bfd8e7b95eb1d8d0b87781d4ffea4d5d"
    assert (
        hash(hello, algo="sha256")
        == "1894a19c85ba153acbf743ac4e43fc004c891604b26f8c69e1e83ea2afc7c48f"
    )


def test_first_chunk(fs):
    hello = Path("hello.txt")
    hello.write_text("Hello world\n")
    hash_hello = hash_first_chunk(hello, algo="md5")
    assert hash_hello == "f0ef7081e1539ac00ef5b761b4fb01b3"

    long_asd = Path("long_asd.txt")
    long_asd.write_text("asd" * 10000)
    hash_asd = hash_first_chunk(long_asd, algo="sha1")

    long_foo = Path("long_foo.txt")
    long_foo.write_text("foo" * 10000)
    hash_foo = hash_first_chunk(long_foo, algo="sha1")

    assert hash_asd != hash_foo != hash_hello

    # make sure only the first chunk is used
    long_foo.write_text("foo" * 10001)
    assert hash_foo == hash_first_chunk(long_foo, algo="sha1")


def test_hash(fs, testoutput):
    make_files({"hello.txt": "Hello world\n"}, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            filters:
              - hash
            actions:
              - echo: "File hash: {hash}"
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["File hash: f0ef7081e1539ac00ef5b761b4fb01b3"]
