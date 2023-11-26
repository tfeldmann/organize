from conftest import make_files, read_files

from organize import Config


def test_python(fs, testoutput):
    make_files(
        ["student-01.jpg", "student-01.txt", "student-02.txt", "student-03.txt"],
        "test",
    )
    config = """
        rules:
        - locations: /test
          filters:
            - name
            - extension: txt
            - python: |
                return int(name.split('.')[0][-2:]) * 100
          actions:
            - echo: '{python}'
        """
    Config.from_string(config).execute(simulate=False, output=testoutput)
    assert testoutput.messages == [
        "100",
        "200",
        "300",
    ]


def test_odd_detector(fs, testoutput):
    make_files(
        ["student-01.txt", "student-02.txt", "student-03.txt", "student-04.txt"],
        "test",
    )
    config = """
        rules:
        - locations: /test
          filters:
            - name
            - python: |
                return int(name.split('-')[1]) % 2 == 1
          actions:
            - echo: 'Odd student numbers: {name}'
        """
    Config.from_string(config).execute(simulate=False, output=testoutput)
    assert testoutput.messages == [
        "Odd student numbers: student-01",
        "Odd student numbers: student-03",
    ]


def test_python_dict(fs, testoutput):
    make_files(
        ["foo-01.jpg", "foo-01.txt", "bar-02.txt", "baz-03.txt"],
        "test",
    )
    config = """
        rules:
          - locations: /test
            filters:
            - extension: txt
            - name
            - python: |
                return {
                    "name": name[:3],
                    "code": int(name.split('.')[0][-2:]) * 100,
                }
            actions:
            - echo: '{python.code} {python.name}'
        """
    Config.from_string(config).execute(simulate=False, output=testoutput)
    assert testoutput.messages == [
        "100 foo",
        "200 bar",
        "300 baz",
    ]


def test_name_reverser(fs):
    make_files(["desrever.jpg", "emanelif.txt"], "test")
    config = """
        rules:
          - locations: /test
            filters:
            - extension
            - name
            - python: |
                return {
                    "reversed_name": name[::-1],
                }
            actions:
            - rename: '{python.reversed_name}.{extension}'
        """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "reversed.jpg": "",
        "filename.txt": "",
    }


def test_folder_instructions(fs):
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
    make_files(
        [
            "2019_Jobs_CategoryA_TagB_A-Media_content-name_V01_draft_eng.docx",
            "2019_Work_CategoryC_V-Test_A-Audio_V14_final.pdf",
            "other.pdf",
        ],
        "test",
    )
    config = r"""
        rules:
            - locations: /test
              filters:
                - extension:
                    - pdf
                    - docx
                - name:
                    contains: "_"
                - python: |
                    import os
                    parts = ["/test"]
                    instructions = dict()
                    for part in name.split("_"):
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
                - move: "{python.new_path}/{name}.{extension}"
        """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "other.pdf": "",
        "2019": {
            "Jobs": {
                "CategoryA": {
                    "TagB": {
                        "V01": {
                            "draft": {
                                "eng": {
                                    "2019_Jobs_CategoryA_TagB_A-Media_content-name_V01_draft_eng.docx": "",
                                }
                            }
                        }
                    }
                }
            },
            "Work": {
                "CategoryC": {
                    "V14": {
                        "final": {
                            "2019_Work_CategoryC_V-Test_A-Audio_V14_final.pdf": "",
                        }
                    }
                }
            },
        },
    }
