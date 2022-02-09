import fs
from conftest import make_files, read_files, rules_shortcut

from organize import core


def test_rename_issue52():
    # test for issue https://github.com/tfeldmann/organize/issues/51
    files = {
        "files": {
            "19asd_WF_test2.PDF": "",
            "other.pdf": "",
            "18asd_WFX_test2.pdf": "",
        }
    }
    with fs.open_fs("temp://") as mem:
        make_files(mem, files)
        config = rules_shortcut(
            mem,
            filters="""
            - extension
            - name:
                startswith: "19"
                contains:
                    - "_WF_"
            """,
            actions=[
                {"rename": "{path.stem}_unread.{extension.lower()}"},
                {"copy": {"dest": "files/copy/", "filesystem": mem}},
            ],
        )
        core.run(config, simulate=False)
        mem.tree()
        result = read_files(mem)

        assert result == {
            "files": {
                "copy": {
                    "19asd_WF_test2_unread.pdf": "",
                },
                "19asd_WF_test2_unread.pdf": "",
                "other.pdf": "",
                "18asd_WFX_test2.pdf": "",
            }
        }
