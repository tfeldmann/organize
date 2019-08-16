from conftest import assertdir, create_filesystem
from organize.cli import main


def test_codepost_usecase(tmp_path):
    create_filesystem(
        tmp_path,
        files=[
            "Devonte-Betts.txt",
            "Alaina-Cornish.txt",
            "Dimitri-Bean.txt",
            "Lowri-Frey.txt",
            "Someunknown-User.txt",
        ],
        config=r"""
        rules:
        - folders: files
          filters:
            - regex: (?P<firstname>\w+)-(?P<lastname>\w+)\..*
            - python: |
                emails = {
                    "Betts": "dbetts@mail.de",
                    "Cornish": "acornish@google.com",
                    "Bean": "dbean@aol.com",
                    "Frey": "l-frey@frey.org",
                }
                if regex.lastname in emails: # get emails from wherever
                    return {"mail": emails[regex.lastname]}
          actions:
            - rename: '{python.mail}.txt'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "dbetts@mail.de.txt",
        "acornish@google.com.txt",
        "dbean@aol.com.txt",
        "l-frey@frey.org.txt",
        "Someunknown-User.txt",  # no email found
    )
