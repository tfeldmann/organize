from conftest import make_files, read_files

from organize import Config

structure = {
    "file1.txt": "",
    "file2.txt": "",
}


def test_simple_replace(fs):
    make_files(structure, "/test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            subfolders: true
            actions:
            - rename: "{path.name.replace('file', 'Datei')}"
        """
    ).execute(simulate=False)
    assert read_files("/test") == {
        "Datei1.txt": "",
        "Datei2.txt": "",
    }
