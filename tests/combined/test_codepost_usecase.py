from conftest import make_files, read_files

from organize import Config


def test_codepost_usecase(fs):
    files = {
        "Devonte-Betts.txt": "",
        "Alaina-Cornish.txt": "",
        "Dimitri-Bean.txt": "",
        "Lowri-Frey.txt": "",
        "Someunknown-User.txt": "",
    }
    make_files(files, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            filters:
              - extension: txt
              - regex: (?P<firstname>\w+)-(?P<lastname>\w+)..*
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
              - move: "/files/{python.mail}.txt"
        """
    ).execute(simulate=False)
    result = read_files("/files")
    assert result == {
        "dbetts@mail.de.txt": "",
        "acornish@google.com.txt": "",
        "dbean@aol.com.txt": "",
        "l-frey@frey.org.txt": "",
    }
