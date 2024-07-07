from conftest import make_files, read_files

from organize import Config

structure = {
    "file1.txt": "",
    "file2.txt": "",
    "folder1": {
        "folder2": {
            "file1.2.1.txt": "",
            "file1.2.2.txt": "",
        },
        "file1.1.txt": "",
        "file1.2.txt": "",
    },
}


def test_parent_folder_only(fs):
    make_files(structure, "/test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            subfolders: true
            filters:
            - name:
                startswith: file
            actions:
            - copy: "/dest/{path.parent.name}/"
        """
    ).execute(simulate=False)
    assert read_files("/dest") == {
        "test": {
            "file1.txt": "",
            "file2.txt": "",
        },
        "folder1": {
            "file1.1.txt": "",
            "file1.2.txt": "",
        },
        "folder2": {
            "file1.2.1.txt": "",
            "file1.2.2.txt": "",
        },
    }


def test_from_monitoring_folder(fs):
    make_files(structure, "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            subfolders: true
            filters:
            - name:
                startswith: file
            actions:
            - copy: "/dest/{relative_path}"
        """
    ).execute(simulate=False)
    assert read_files("dest") == structure


def test_from_root(fs):
    make_files(structure, "/test/sub1/sub2")
    Config.from_string(
        """
        rules:
          - locations: "/test/sub1"
            subfolders: true
            filters:
            - name:
                startswith: file
            actions:
            - copy: "/dest/{path}"
        """
    ).execute(simulate=False)
    assert read_files("/dest") == {"test": {"sub1": {"sub2": structure}}}
