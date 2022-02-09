import fs
from conftest import make_files, read_files, rules_shortcut

from organize import core

CONTENT_SMALL = "COPY CONTENT"
CONTENT_LARGE = "XYZ" * 3000


def test_duplicate_smallfiles():
    files = {
        "files": {
            "unique.txt": "I'm unique.",
            "unique_too.txt": "I'm unique: too.",
            "a.txt": CONTENT_SMALL,
            "copy2.txt": CONTENT_SMALL,
            "other": {
                "copy.txt": CONTENT_SMALL,
                "copy.jpg": CONTENT_SMALL,
                "large.txt": CONTENT_LARGE,
            },
            "large_unique.txt": CONTENT_LARGE,
        },
    }

    with fs.open_fs("mem://") as mem:
        make_files(mem, files)
        rules = rules_shortcut(
            mem,
            filters="- duplicate",
            actions="- echo: '{fs_path} is duplicate of {duplicate}'\n- delete",
            max_depth=None,
        )
        core.run(rules, simulate=False, validate=False)
        result = read_files(mem)
        mem.tree()
        assert result == {
            "files": {
                "unique.txt": "I'm unique.",
                "unique_too.txt": "I'm unique: too.",
                "a.txt": CONTENT_SMALL,
                "other": {
                    "large.txt": CONTENT_LARGE,
                },
            },
        }


#     main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
#     assertdir(tmp_path,)


# def test_duplicate_largefiles(tmp_path):
#     create_filesystem(
#         tmp_path,
#         files=[
#             ("unique.txt", CONTENT_LARGE + "1"),
#             ("unique_too.txt", CONTENT_LARGE + "2"),
#             ("a.txt", CONTENT_LARGE),
#             ("copy2.txt", CONTENT_LARGE),
#             ("other/copy.txt", CONTENT_LARGE),
#             ("other/copy.jpg", CONTENT_LARGE),
#             ("other/large.txt", CONTENT_LARGE),
#         ],
#         config="""
#         rules:
#         - folders: files
#           subfolders: true
#           filters:
#             - duplicate
#           actions:
#             - trash
#         """,
#     )
#     main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
#     assertdir(tmp_path, "unique.txt", "unique_too.txt", "a.txt")
