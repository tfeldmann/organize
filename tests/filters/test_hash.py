from pathlib import Path

from conftest import make_files

from organize import Config
from organize.filters.hash import hash, hash_first_chunk


def test_full_hash(fs):
    r"""
    Reference hashsums:

    ```sh
    python3 -c 'from pathlib import Path; Path("hello.txt").write_text("Hello world")'
    md5 hello.txt && shasum -a1 hello.txt && shasum -a256 hello.txt
    ```

    Do not use newlines in the textfiles. In windows a newline is \r\n, unix: \n.
    """
    hello = Path("hello.txt")
    hello.write_text("Hello world")
    assert hash(hello, algo="md5") == "3e25960a79dbc69b674cd4ec67a72c62"
    assert hash(hello, algo="sha1") == "7b502c3a1f48c8609ae212cdfb639dee39673f5e"
    assert (
        hash(hello, algo="sha256")
        == "64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232534a8aeca37f3c"
    )


def test_first_chunk(fs):
    hello = Path("hello.txt")
    hello.write_text("Hello world")
    hash_hello = hash_first_chunk(hello, algo="md5")
    assert hash_hello == "3e25960a79dbc69b674cd4ec67a72c62"

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
    make_files({"hello.txt": "Hello world"}, "test")
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
    assert testoutput.messages == ["File hash: 3e25960a79dbc69b674cd4ec67a72c62"]
