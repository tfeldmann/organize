from conftest import create_filesystem, assertdir
from organize.cli import main


def test_startswith_issue74(tmp_path):
    # test for issue https://github.com/tfeldmann/organize/issues/74
    create_filesystem(
        tmp_path,
        files=["Cálculo_1.pdf", "Cálculo_2.pdf", "Calculo.pdf",],
        config=r"""
        # Cálculo PDF
        rules:
            - folders: files
              filters:
                - extension:
                    - pdf
                - filename:
                    startswith: Cálculo
              actions:
                - move: "files/Cálculo Integral/Periodo #6/PDF's/"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "Cálculo Integral/Periodo #6/PDF's/Cálculo_1.pdf",
        "Cálculo Integral/Periodo #6/PDF's/Cálculo_2.pdf",
        "Calculo.pdf",
    )
