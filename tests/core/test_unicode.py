from pathlib import Path

import pytest
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


CONFUSABLES = (
    (
        b"Ertr\xc3\xa4gnisaufstellung".decode("utf-8"),
        b"Ertra\xcc\x88gnisaufstellung".decode("utf-8"),
    ),
    (
        b"Ertra\xcc\x88gnisaufstellung".decode("utf-8"),
        b"Ertr\xc3\xa4gnisaufstellung".decode("utf-8"),
    ),
)


@pytest.mark.parametrize("a, b", CONFUSABLES)
def test_normalize(a, b):
    assert a != b
    assert normalize_unicode(a) == normalize_unicode(b)


@pytest.mark.parametrize("a, b", CONFUSABLES)
def test_normalization_regex(fs, a, b):
    make_files({f"{a}.txt": ""}, "test")
    config = f"""
    rules:
      - locations: /test
        filters:
          - regex: {b}
        actions:
          - rename: "found-regex.txt"
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {"found-regex.txt": ""}


@pytest.mark.parametrize("a, b", CONFUSABLES)
def test_normalization_filename(fs, a, b):
    make_files({f"{a}.txt": ""}, "test")
    config = f"""
    rules:
      - locations: /test
        filters:
          - name: {a}
        actions:
          - rename: "found-regex.txt"
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {"found-regex.txt": ""}
