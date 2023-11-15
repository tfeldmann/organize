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


# TODO
# def test_shell_basic():
#     shell = Shell(
#         "echo 'Hello World'",
#         simulation_output="-sim-",
#         simulation_returncode=127,
#     )
#     result = shell.run(simulate=True)
#     assert "-sim-" in result["shell"]["output"]
#     assert 127 == result["shell"]["returncode"]

#     result = shell.run(simulate=False)
#     result = result["shell"]
#     assert "Hello World" in result["output"]  # windows escapes the string
#     assert result["returncode"] == 0


# def test_shell_template_simulation():
#     shell = Shell("echo '{msg}'", run_in_simulation=True)
#     result = shell.run(msg="Hello", simulate=True)
#     result = result["shell"]
#     assert "Hello" in result["output"]
#     assert result["returncode"] == 0
