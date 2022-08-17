import os

import fs
from click.testing import CliRunner
from conftest import make_files
from fs.base import FS

from organize import cli

runner = CliRunner()


def test_config_file(tempfs: FS):
    files = ["my-test-file-name.txt", "my-test-file-name.jpg", "other-file.txt"]
    make_files(tempfs, files)
    config = """
    rules:
      - locations: %s
        filters:
          - name: my-test-file-name
        actions:
          - delete
    """
    with fs.open_fs("temp://") as configfs:
        configfs.writetext("config.yaml", config % tempfs.getsyspath("/"))
        args = [configfs.getsyspath("config.yaml")]
        result = runner.invoke(cli.sim, args)
        print(result.output)
        assert result.exit_code == 0
        assert set(tempfs.listdir("/")) == set(files)
        result = runner.invoke(cli.run, args)
        print(result.output)
        assert result.exit_code == 0
        assert set(tempfs.listdir("/")) == set(["other-file.txt"])


def test_working_dir(tempfs: FS):
    files = ["my-test-file-name.txt", "my-test-file-name.jpg", "other-file.txt"]
    make_files(tempfs, files)
    config = """
    rules:
      - locations: "."
        filters:
          - name: my-test-file-name
        actions:
          - delete
    """
    with fs.open_fs("temp://") as configfs:
        configfs.writetext("config.yaml", config)
        args = [
            configfs.getsyspath("config.yaml"),
            "--working-dir=%s" % tempfs.getsyspath("/"),
        ]
        print(args)
        runner.invoke(cli.sim, args)
        assert set(tempfs.listdir("/")) == set(files)
        runner.invoke(cli.run, args)
        assert set(tempfs.listdir("/")) == set(["other-file.txt"])


def test_with_os_chdir(tempfs: FS):
    files = ["my-test-file-name.txt", "my-test-file-name.jpg", "other-file.txt"]
    make_files(tempfs, files)
    config = """
    rules:
      - locations: "."
        filters:
          - name: my-test-file-name
        actions:
          - delete
    """
    with fs.open_fs("temp://") as configfs:
        configfs.writetext("config.yaml", config)
        args = [
            configfs.getsyspath("config.yaml"),
        ]
        print(args)
        os.chdir(tempfs.getsyspath("/"))
        runner.invoke(cli.sim, args)
        assert set(tempfs.listdir("/")) == set(files)
        runner.invoke(cli.run, args)
        assert set(tempfs.listdir("/")) == set(["other-file.txt"])
