import fs
from conftest import make_files, read_files

from organize import actions, config, core


def test_codepost_usecase():
    files = {
        "files": {
            "Devonte-Betts.txt": "",
            "Alaina-Cornish.txt": "",
            "Dimitri-Bean.txt": "",
            "Lowri-Frey.txt": "",
            "Someunknown-User.txt": "",
        }
    }
    conf = config.load_from_string(
        r"""
        rules:
        - locations: files
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
    """
    )
    with fs.open_fs("mem://") as mem:
        conf["actions"] = actions.Move("{python.mail}.txt", filesystem=mem)
        make_files(mem, files)
        print(conf)
        core.run(mem, conf, simulate=False)
        result = read_files(mem)
        mem.tree()

    assert result == {
        "files": {
            "dbetts@mail.de.txt": "",
            "acornish@google.com.txt": "",
            "dbean@aol.com.txt": "",
            "l-frey@frey.org.txt": "",
            "Someunknown-User.txt": "",
        }
    }
