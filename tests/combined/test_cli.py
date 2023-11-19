# from conftest import assertdir, create_filesystem

# from organize.cli import main


# def test_filename_move(tmp_path):
#     create_filesystem(
#         tmp_path,
#         files=["test.PY"],
#         config="""
#             rules:
#             - folders: files
#               filters:
#               - Extension
#               actions:
#               - rename: '{path.stem}{path.stem}.{extension.lower}'
#         """,
#     )
#     main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
#     assertdir(tmp_path, "testtest.py")


# def test_basic(tmp_path):
#     create_filesystem(
#         tmp_path,
#         files=["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"],
#         config="""
#             rules:
#             - folders: files
#               filters:
#                 - filename: test
#               actions:
#                 - copy: files/newname.pdf
#         """,
#     )
#     main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
#     assertdir(
#         tmp_path, "newname.pdf", "newname 2.pdf", "newname 3.pdf", "test.pdf", "asd.txt"
#     )


# @pytest.mark.skip
# def test_config_file(tempfs: FS):
#     files = ["my-test-file-name.txt", "my-test-file-name.jpg", "other-file.txt"]
#     make_files(tempfs, files)
#     config = """
#     rules:
#       - locations: %s
#         filters:
#           - name: my-test-file-name
#         actions:
#           - delete
#     """
#     with fs.open_fs("temp://") as configfs:
#         configfs.writetext("config.yaml", config % tempfs.getsyspath("/"))
#         args = [configfs.getsyspath("config.yaml")]
#         result = runner.invoke(cli.sim, args)
#         print(result.output)
#         assert set(tempfs.listdir("/")) == set(files)
#         result = runner.invoke(cli.run, args)
#         print(result.output)
#         assert set(tempfs.listdir("/")) == set(["other-file.txt"])


# @pytest.mark.skip
# def test_working_dir(tempfs: FS):
#     files = ["my-test-file-name.txt", "my-test-file-name.jpg", "other-file.txt"]
#     make_files(tempfs, files)
#     config = """
#     rules:
#       - locations: "."
#         filters:
#           - name: my-test-file-name
#         actions:
#           - delete
#     """
#     with fs.open_fs("temp://") as configfs:
#         configfs.writetext("config.yaml", config)
#         args = [
#             configfs.getsyspath("config.yaml"),
#             "--working-dir=%s" % tempfs.getsyspath("/"),
#         ]
#         print(args)
#         runner.invoke(cli.sim, args)
#         assert set(tempfs.listdir("/")) == set(files)
#         runner.invoke(cli.run, args)
#         assert set(tempfs.listdir("/")) == set(["other-file.txt"])


# @pytest.mark.skip
# def test_with_os_chdir(tempfs: FS):
#     files = ["my-test-file-name.txt", "my-test-file-name.jpg", "other-file.txt"]
#     make_files(tempfs, files)
#     config = """
#     rules:
#       - locations: "."
#         filters:
#           - name: my-test-file-name
#         actions:
#           - delete
#     """
#     with fs.open_fs("temp://") as configfs:
#         configfs.writetext("config.yaml", config)
#         args = [
#             configfs.getsyspath("config.yaml"),
#         ]
#         print(args)
#         os.chdir(tempfs.getsyspath("/"))
#         runner.invoke(cli.sim, args)
#         assert set(tempfs.listdir("/")) == set(files)
#         runner.invoke(cli.run, args)
#         assert set(tempfs.listdir("/")) == set(["other-file.txt"])
