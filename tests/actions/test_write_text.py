from conftest import make_files


def test_append(testfs):
    files = ["a.txt", "b.txt", "c.txt"]
    make_files(testfs, files)
    config = """
    rules:
      - locations: .
        actions:
          - write_text:

    """
