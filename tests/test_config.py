import pytest

from organize.config import Config, Rule
from organize.filters import Extension, LastModified
from organize.actions import Move, Echo, Shell, Trash


def test_basic():
    config = """
    rules:
      - folders: '~/Desktop'
        filters:
          - Extension:
            - jpg
            - png
          - Extension: txt
        actions:
          - Move: {dest: '~/Desktop/New Folder', overwrite: true}
          - Echo: 'Moved {path}/{extension.upper}'
      - folders:
          - '~/test1'
          - /test2
        filters:
        actions:
          - Shell:
              cmd: 'say {path.stem}'
    """
    conf = Config.from_string(config)
    assert conf.rules == [
        Rule(
            folders=["~/Desktop"],
            filters=[Extension(".JPG", "PNG"), Extension("txt")],
            actions=[
                Move(dest="~/Desktop/New Folder", overwrite=True),
                Echo(msg="Moved {path}/{extension.upper}"),
            ],
            subfolders=False,
            system_files=False,
        ),
        Rule(
            folders=["~/test1", "/test2"],
            filters=[],
            actions=[Shell(cmd="say {path.stem}")],
            subfolders=False,
            system_files=False,
        ),
    ]


def test_lowercase():
    config = """
    rules:
      - folders: '~/Desktop'
        filters:
          - extension:
            - jpg
            - png
          - extension: txt
        actions:
          - move: {dest: '~/Desktop/New Folder', overwrite: true}
          - EC_HO: 'Moved {path}/{extension.upper}'
      - folders:
          - '~/test1'
          - /test2
        filters:
        actions:
          - SHELL:
              cmd: 'say {path.stem}'
    """
    conf = Config.from_string(config)
    assert conf.rules == [
        Rule(
            folders=["~/Desktop"],
            filters=[Extension(".JPG", "PNG"), Extension("txt")],
            actions=[
                Move(dest="~/Desktop/New Folder", overwrite=True),
                Echo(msg="Moved {path}/{extension.upper}"),
            ],
            subfolders=False,
            system_files=False,
        ),
        Rule(
            folders=["~/test1", "/test2"],
            filters=[],
            actions=[Shell(cmd="say {path.stem}")],
            subfolders=False,
            system_files=False,
        ),
    ]


def test_yaml_ref():
    config = """
    media: &media
      - wav
      - png

    all_folders: &all
      - ~/Desktop
      - ~/Documents

    rules:
      - folders: *all
        filters:
          - Extension: *media
          - Extension:
            - *media
            - jpg
          - LastModified:
              days: 10
        actions:
          - Echo:
              msg: 'Hello World'
      - folders:
          - *all
          - /more/more
        filters:
        actions:
          - Trash
    """
    conf = Config.from_string(config)
    assert conf.rules == [
        Rule(
            folders=["~/Desktop", "~/Documents"],
            filters=[
                Extension(".wav", ".PNG"),
                Extension(".wav", ".PNG", "jpg"),
                LastModified(days=10),
            ],
            actions=[Echo(msg="Hello World")],
            subfolders=False,
            system_files=False,
        ),
        Rule(
            folders=["~/Desktop", "~/Documents", "/more/more"],
            filters=[],
            actions=[Trash()],
            subfolders=False,
            system_files=False,
        ),
    ]


def test_error_filter_dict():
    conf = Config.from_string(
        """
    rules:
      - folders: '/'
        filters:
          Extension: 'jpg'
        actions:
          - Trash
    """
    )
    with pytest.raises(Config.FiltersNoListError):
        _ = conf.rules


def test_error_action_dict():
    conf = Config.from_string(
        """
    rules:
      - folders: '/'
        filters:
          - Extension: 'jpg'
        actions:
          Trash
    """
    )
    with pytest.raises(Config.ActionsNoListError):
        _ = conf.rules


def test_empty_filters():
    conf = """
    rules:
      - folders: '/'
        filters:
        actions:
          - Trash
      - folders: '~/'
        actions:
          - Trash
    """
    assert Config.from_string(conf).rules == [
        Rule(
            folders=["/"],
            filters=[],
            actions=[Trash()],
            subfolders=False,
            system_files=False,
        ),
        Rule(
            folders=["~/"],
            filters=[],
            actions=[Trash()],
            subfolders=False,
            system_files=False,
        ),
    ]
