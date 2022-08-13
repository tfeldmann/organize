from fs import open_fs
from fs import copy

from organize.core import run


def test_folder_renaming():
    config = """
rules:
  - name: "Renaming DVD folders"
    locations:
      - path: %s
        max_depth: null
    targets: dirs
    subfolders: true
    filters:
      - name:
          contains: DVD
    actions:
      - echo: "{path}"
      - rename:
          name: "{name.replace('[DVD] ','').replace(' [1080p]','').replace(' ', '_')}"
          on_conflict: "overwrite"
"""
    with open_fs("temp://") as fs:
        copy.copy_dir("tests/resources", "dvds", fs, "/")
        run(rules=config % fs.getsyspath("."), simulate=False, validate=True)
        assert fs.exists("Best_Of_Video_1080")
        assert fs.getinfo("Best_Of_Video_1080").is_dir
        assert fs.exists("This_Is_A_Title")
        assert fs.getinfo("This_Is_A_Title").is_dir
