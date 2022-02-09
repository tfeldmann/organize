from unittest.mock import call

from conftest import assertdir, create_filesystem

from organize.cli import main


def test_python(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["student-01.jpg", "student-01.txt", "student-02.txt", "student-03.txt"],
        config="""
        rules:
        - folders: files
          filters:
            - extension: txt
            - python: |
                return int(path.name.split('.')[0][-2:]) * 100
          actions:
            - echo: '{python}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("100"),
            call("200"),
            call("300"),
        ),
        any_order=True,
    )


def test_odd_detector(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["student-01.txt", "student-02.txt", "student-03.txt", "student-04.txt"],
        config="""
        rules:
        - folders: files
          filters:
            - python: |
                return int(path.stem.split('-')[1]) % 2 == 1
          actions:
            - echo: 'Odd student numbers: {path.name}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("Odd student numbers: student-01.txt"),
            call("Odd student numbers: student-03.txt"),
        ),
        any_order=True,
    )


def test_python_dict(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["foo-01.jpg", "foo-01.txt", "bar-02.txt", "baz-03.txt"],
        config="""
        rules:
          - folders: files
            filters:
            - extension: txt
            - python: |
                return {
                    "name": path.name[:3],
                    "code": int(path.name.split('.')[0][-2:]) * 100,
                }
            actions:
            - echo: '{python.code} {python.name}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("100 foo"),
            call("200 bar"),
            call("300 baz"),
        ),
        any_order=True,
    )


def test_name_reverser(tmp_path):
    create_filesystem(
        tmp_path,
        files=["desrever.jpg", "emanelif.txt"],
        config="""
        rules:
          - folders: files
            filters:
            - extension
            - python: |
                return {
                    "reversed_name": path.stem[::-1],
                }
            actions:
            - rename: '{python.reversed_name}.{extension}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "reversed.jpg", "filename.txt")


def test_folder_instructions(tmp_path):
    """
    I would like to include path/folder-instructions into the filename because I have a
    lot of different files (and there are always new categories added) I don't want
    create rules for. For example my filename is

    '2019_Jobs_CategoryA_TagB_A-Media_content-name_V01_draft_eng.docx'

    which means: Move the file to the folder '2019/Jobs/CategoryA/TagB/Media/drafts/eng'
    whereby 'A-' is an additional instruction and should be removed from the filename
    afterwards ('2019_Jobs_CategoryA_TagB_content-name_V01_draft_eng.docx').

    I have a rough idea to figure it out with python but I'm new to it (see below a
    sketch). Is there a possibility to use such variables, conditions etc. with
    organizer natively? If no, is it possible to do it with Python in Organizer at all?

     - Transform file-string into array
     - Search for 'A-...', 'V...' and 'content-name' and get index of values
     - remove value 'A-... and 'content-name' of array
     - build new filename string
     - remove value 'V...' and 'A-' of array
     - build folder-path string (convert _ to /) etc.

    """
    # inspired by: https://github.com/tfeldmann/organize/issues/52
    create_filesystem(
        tmp_path,
        files=[
            "2019_Jobs_CategoryA_TagB_A-Media_content-name_V01_draft_eng.docx",
            "2019_Work_CategoryC_V-Test_A-Audio_V14_final.pdf",
            "other.pdf",
        ],
        config=r"""
        rules:
            - folders: files
              filters:
                - extension:
                    - pdf
                    - docx
                - filename:
                    contains: "_"
                - python: |
                    import os
                    parts = []
                    instructions = dict()
                    for part in path.stem.split("_"):
                        if part.startswith("A-"):
                            instructions["A"] = part[2:]
                        elif part.startswith("V-"):
                            instructions["V"] = part[2:]
                        elif part.startswith("content-name"):
                            instructions["content"] = part[12:]
                        else:
                            parts.append(part)
                    return {
                        "new_path": os.path.join(*parts),
                        "instructions": instructions,
                    }
              actions:
                - echo: "New path: {python.new_path}"
                - echo: "Instructions: {python.instructions}"
                - echo: "Value of A: {python.instructions.A}"
                - move: "files/{python.new_path}/{path.name}"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "other.pdf",
        "2019/Jobs/CategoryA/TagB/V01/draft/eng/2019_Jobs_CategoryA_TagB_A-Media_content-name_V01_draft_eng.docx",
        "2019/Work/CategoryC/V14/final/2019_Work_CategoryC_V-Test_A-Audio_V14_final.pdf",
        "other.pdf",
    )
