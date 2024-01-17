from pathlib import Path

from conftest import make_files, read_files

from organize import Config
from organize.utils import normalize_unicode


def test_startswith_issue74(fs):
    # test for issue https://github.com/tfeldmann/organize/issues/74
    make_files(
        {
            "Cálculo_1.pdf": "",
            "Cálculo_2.pdf": "",
            "Calculo.pdf": "",
        },
        "test",
    )
    config = r"""
        # Cálculo PDF
        rules:
            - locations: /test
              filters:
                - extension:
                    - pdf
                - name:
                    startswith: Cálculo
              actions:
                - move: "/test/Cálculo Integral/Periodo #6/PDF's/"
        """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "Cálculo Integral": {
            "Periodo #6": {
                "PDF's": {
                    "Cálculo_1.pdf": "",
                    "Cálculo_2.pdf": "",
                }
            }
        },
        "Calculo.pdf": "",
    }


def test_folder_umlauts(fs):
    make_files(["file1", "file2"], "Erträge")

    conf = Path("config.yaml")
    conf.write_text(
        """
    rules:
      - locations: "Erträge"
        actions:
          - delete
    """,
        encoding="utf-8",
    )
    Config.from_path(conf).execute(simulate=False)
    assert read_files("Erträge") == {}


def test_normalize():
    formA = b"Ertr\xc3\xa4gnisaufstellung.txt".decode("utf-8")  # copied from config
    formB = b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8")  # copied from filename
    assert normalize_unicode(formA) == normalize_unicode(formB)


def test_normalization_regex(fs):
    make_files(
        {b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8"): ""},
        "test",
    )
    config = (
        b"""
    rules:
      - locations: /test
        filters:
          - regex: 'Ertr\xc3\xa4gnisaufstellung.txt$'
        actions:
          - rename: "found-regex.txt"
    """
    ).decode("utf-8")
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {"found-regex.txt"}


def test_normalization_filename(fs):
    make_files(
        {b"Ertr\xcc\x88gnisaufstellung.txt".decode("utf-8"): ""},
        "test",
    )
    config = (
        b"""
    rules:
      - locations: /test
        filters:
          - name: "Ertr\xc3\xa4gnisaufstellung"
        actions:
          - rename: "found-regex.txt"
    """
    ).decode("utf-8")
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {"found-regex.txt"}
