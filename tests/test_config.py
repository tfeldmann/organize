import pytest

from organize.config import Config, Rule
from organize.filters import Extension, PaperVDI
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
          - Echo: 'Moved {path}{extension.upper}'
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
            folders=['~/Desktop'],
            filters=[Extension('.JPG', 'PNG'), Extension('txt')],
            actions=[
                Move(dest='~/Desktop/New Folder', overwrite=True),
                Echo(msg='Moved {path}{extension.upper}')
            ]
        ),
        Rule(
            folders=['~/test1', '/test2'],
            filters=[],
            actions=[Shell(cmd='say {path.stem}')]
        )
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
          - PaperVDI
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
            folders=['~/Desktop', '~/Documents'],
            filters=[
                Extension('.wav', '.PNG'),
                Extension('.wav', '.PNG', 'jpg'),
                PaperVDI()],
            actions=[
                Echo(msg='Hello World')]
        ),
        Rule(
            folders=['~/Desktop', '~/Documents', '/more/more'],
            filters=[],
            actions=[Trash()]
        )
    ]


def test_error_filter_dict():
    conf = Config.from_string("""
    rules:
      - folders: '/'
        filters:
          Extension: 'jpg'
        actions:
          - Trash
    """)
    with pytest.raises(Config.FiltersNoListError):
        _ = conf.rules


def test_error_action_dict():
    conf = Config.from_string("""
    rules:
      - folders: '/'
        filters:
          - Extension: 'jpg'
        actions:
          Trash
    """)
    with pytest.raises(Config.ActionsNoListError):
        _ = conf.rules


def test_empty_filters():
    conf = Config.from_string("""
    rules:
      - folders: '/'
        filters:
        actions:
          - Trash
      - folders: '~/'
        actions:
          - Trash
    """)
    assert conf.rules == [
        Rule(
            folders=['/'],
            filters=[],
            actions=[Trash()]
        ),
        Rule(
            folders=['~/'],
            filters=[],
            actions=[Trash()]
        )
    ]
