from collections import Counter
from pathlib import Path

from organize.config import Config


def test_codepost_usecase(fs):
    fs.create_file("files/Devonte-Betts.txt")
    fs.create_file("files/Alaina-Cornish.txt")
    fs.create_file("files/Dimitri-Bean.txt")
    fs.create_file("files/Lowri-Frey.txt")
    fs.create_file("files/Someunknown-User.txt")

    Config.from_string(
        """
        rules:
            -   locations: files
                filters:
                    - extension: txt
                    - regex: (?P<firstname>\w+)-(?P<lastname>\w+)\..*
                    - python: |
                        emails = {
                            "Betts": "dbetts@mail.de",
                            "Cornish": "acornish@google.com",
                            "Bean": "dbean@aol.com",
                            "Frey": "l-frey@frey.org",
                        }
                        if regex["lastname"] in emails:
                            return {"mail": emails[regex["lastname"]]}
                actions:
                    - move: "files/{python.mail}.txt"
        """
    ).execute(simulate=False)
    assert Counter(Path("files").glob("*")) == Counter(
        "files/dbetts@mail.de.txt",
        "files/acornish@google.com.txt",
        "files/dbean@aol.com.txt",
        "files/l-frey@frey.org.txt",
        "files/Someunknown-User.txt",
    )
