from fs import open_fs

def test_already_handled_files():
    with open_fs("temp://") as tmp:
        pass
