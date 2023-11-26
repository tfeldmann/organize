from pathlib import Path

from conftest import make_files

from organize import Config


def test_python(fs, testoutput):
    make_files({"file.txt": "File content"}, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            actions:
              - python: |
                    from pathlib import Path

                    Path("/test/result.txt").touch()
                    print(f"Handling: {path}")
                    return {"content": path.read_text()}
              - echo: "{python.content}"
        """
    ).execute(simulate=False, output=testoutput)
    assert Path("/test/result.txt").exists()
    assert testoutput.messages == [
        "Handling: /test/file.txt",
        "File content",
    ]
