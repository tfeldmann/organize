import pytest
from conftest import make_files, read_files

from organize import Config


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


@pytest.mark.skip(reason="TODO")
def test_normalization_regex(testfs):
    make_files(
        testfs,
        {b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8"): ""},
    )
    config = (
        b"""
    rules:
      - locations: "."
        filters:
          - regex: 'Ertra\xc3\xa4gnisaufstellung.txt$'
        actions:
          - rename: "found-regex.txt"
    """
    ).decode("utf-8")
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {"found-regex.txt"}


@pytest.mark.skip(reason="TODO")
def test_normalization_filename(testfs):
    make_files(
        testfs,
        {b"Ertr\xcc\x88gnisaufstellung.txt".decode("utf-8"): ""},
    )
    config = (
        b"""
    rules:
      - locations: "."
        filters:
          - filename: "Ertr\xc3\xa4gnisaufstellung"
        actions:
          - rename: "found-regex.txt"
    """
    ).decode("utf-8")
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {"found-regex.txt"}
