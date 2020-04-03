import pytest

from organize.actions import Echo, Move, Shell, Trash, Rename
from organize.config import Config, Rule
from organize.filters import Extension, LastModified, FileContent, Filename


def test_basic():
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
      - echo: 'Moved {path}/{extension.upper}'
    - folders:
      - '~/test1'
      - '/test2'
      filters:
      actions:
      - shell:
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


def test_case_insensitive():
    config = """
    rules:
      - folders: '~/Desktop'
        filters:
          - extension: ['JPg', 'png']
          - Extension: txt
        actions:
          - moVe: {dest: '~/Desktop/New Folder', overwrite: true}
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
          - extension: *media
          - extension:
            - *media
            - jpg
          - lastmodified:
              days: 10
        actions:
          - echo:
              msg: 'Hello World'
      - folders:
          - *all
          - /more/more
        filters:
        actions:
          - trash
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
      - trash
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
      - extension: 'jpg'
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
          - trash
      - folders: '~/'
        actions:
          - trash
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


def test_flatten_filters_and_actions():
    config = """
    folder_aliases:
      Downloads: &downloads ~/Downloads/
      Payables_due: &payables_due ~/PayablesDue/
      Payables_paid: &payables_paid ~/Accounting/Expenses/
      Receivables_due: &receivables_due ~/Receivables/
      Receivables_paid: &receivables_paid ~/Accounting/Income/

    defaults:
      filters: &default_filters
        - extension: pdf
        - filecontent: '(?P<date>...)'
      actions: &default_actions
        - echo: 'Dated: {filecontent.date}'
        - echo: 'Stem of filename: {filecontent.stem}'
      post_actions: &default_sorting
        - rename: '{python.timestamp}-{filecontent.stem}.{extension.lower}'
        - move: '{path.parent}/{python.quarter}/'

    rules:
      - folders: *downloads
        filters:
          - *default_filters
          - filecontent: 'Due Date' # regex to id as payable
          - filecontent: '(?P<stem>...)' # regex to extract supplier
        actions:
          - *default_actions
          - move: *payables_due
          - *default_sorting

      - folders: *downloads
        filters:
          - *default_filters
          - filecontent: 'Account: 000000000' # regex to id as receivables due
          - filecontent: '(?P<stem>...)' # regex to extract customer
        actions:
          - *default_actions
          - move: *receivables_due
          - *default_sorting

      - folders: *downloads
        filters:
          - *default_filters
          - filecontent: 'PAID' # regex to id as receivables paid
          - filecontent: '(?P<stem>...)' # regex to extract customer
          - filecontent: '(?P<paid>...)' # regex to extract date paid
          - filename:
              startswith: 2020
        actions:
          - *default_actions
          - move: *receivables_paid
          - *default_sorting
          - rename: '{filecontent.paid}_{filecontent.stem}.{extension}'
    """
    conf = Config.from_string(config)
    assert conf.rules == [
        Rule(
            folders=["~/Downloads/"],
            filters=[
                # default_filters
                Extension("pdf"),
                FileContent(expr="(?P<date>...)"),
                # added filters
                FileContent(expr="Due Date"),
                FileContent(expr="(?P<stem>...)"),
            ],
            actions=[
                # default_actions
                Echo(msg="Dated: {filecontent.date}"),
                Echo(msg="Stem of filename: {filecontent.stem}"),
                # added actions
                Move(dest="~/PayablesDue/", overwrite=False),
                # default_sorting
                Rename(
                    name="{python.timestamp}-{filecontent.stem}.{extension.lower}",
                    overwrite=False,
                ),
                Move(dest="{path.parent}/{python.quarter}/", overwrite=False),
            ],
            subfolders=False,
            system_files=False,
        ),
        Rule(
            folders=["~/Downloads/"],
            filters=[
                # default_filters
                Extension("pdf"),
                FileContent(expr="(?P<date>...)"),
                # added filters
                FileContent(expr="Account: 000000000"),
                FileContent(expr="(?P<stem>...)"),
            ],
            actions=[
                # default_actions
                Echo(msg="Dated: {filecontent.date}"),
                Echo(msg="Stem of filename: {filecontent.stem}"),
                # added actions
                Move(dest="~/Receivables/", overwrite=False),
                # default_sorting
                Rename(
                    name="{python.timestamp}-{filecontent.stem}.{extension.lower}",
                    overwrite=False,
                ),
                Move(dest="{path.parent}/{python.quarter}/", overwrite=False),
            ],
            subfolders=False,
            system_files=False,
        ),
        Rule(
            folders=["~/Downloads/"],
            filters=[
                # default_filters
                Extension("pdf"),
                FileContent(expr="(?P<date>...)"),
                # added filters
                FileContent(expr="PAID"),
                FileContent(expr="(?P<stem>...)"),
                FileContent(expr="(?P<paid>...)"),
                Filename(startswith="2020"),
            ],
            actions=[
                # default_actions
                Echo(msg="Dated: {filecontent.date}"),
                Echo(msg="Stem of filename: {filecontent.stem}"),
                # added actions
                Move(dest="~/Accounting/Income/", overwrite=False),
                # default_sorting
                Rename(
                    name="{python.timestamp}-{filecontent.stem}.{extension.lower}",
                    overwrite=False,
                ),
                Move(dest="{path.parent}/{python.quarter}/", overwrite=False),
                # added actions
                Rename(
                    name="{filecontent.paid}_{filecontent.stem}.{extension}",
                    overwrite=False,
                ),
            ],
            subfolders=False,
            system_files=False,
        ),
    ]

