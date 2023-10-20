from conftest import read_files

from organize import Config
from organize.output import QueueOutput


def test_shell(tmp_path):
    output = QueueOutput()
    (tmp_path / "test.txt").touch()
    Config.from_string(
        f"""
        rules:
          - locations: "{tmp_path}"
            actions:
              - shell: 'touch {{path}}.bak'
        """
    ).execute(simulate=False, output=output)
    assert read_files(tmp_path) == {
        "test.txt": "",
        "test.txt.bak": "",
    }
