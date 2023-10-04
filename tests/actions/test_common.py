from pathlib import Path

from conftest import make_files, read_files

from organize.actions.common.folder_target import (
    prepare_folder_target,
    user_wants_a_folder,
)


def test_user_wants_a_folder():
    assert user_wants_a_folder("/test/", autodetect=False)
    assert not user_wants_a_folder("/test", autodetect=False)
    assert not user_wants_a_folder("/test.asd", autodetect=False)
    assert user_wants_a_folder("/test.asd/", autodetect=False)
    assert not user_wants_a_folder("/some/original/folder/name.txt", autodetect=False)


def test_user_wants_a_folder_autodetect():
    assert user_wants_a_folder("/test/", autodetect=True)
    assert user_wants_a_folder("/test", autodetect=True)
    assert not user_wants_a_folder("/test.asd", autodetect=True)
    assert user_wants_a_folder("/test.asd/", autodetect=True)
    assert not user_wants_a_folder("/some/original/folder/name.txt", autodetect=False)


def test_prepare_folder_target(fs):
    # simulate
    assert prepare_folder_target(
        src_name="dst.txt",
        dst="/test/",
        autodetect_folder=True,
        simulate=True,
    ) == Path("/test/dst.txt")
    assert not Path("/test").exists()
    # for real
    assert prepare_folder_target(
        src_name="dst.txt",
        dst="/test/",
        autodetect_folder=True,
        simulate=False,
    ) == Path("/test/dst.txt")
    assert read_files("test") == {}


def test_prepare_folder_target_advanced(fs):
    assert prepare_folder_target(
        src_name="dst",
        dst="/some/test/folder",
        autodetect_folder=True,
        simulate=False,
    ) == Path("/some/test/folder/dst")
    assert read_files("some") == {"test": {"folder": {}}}


def test_prepare_folder_target_already_exists(fs):
    make_files({"some": {"Application.app": {}}})
    assert prepare_folder_target(
        src_name="info.plist",
        dst="/some/Application.app",
        autodetect_folder=True,
        simulate=False,
    ) == Path("/some/Application.app/info.plist")
    assert read_files("some") == {"Application.app": {}}


def test_prepare_folder_no_folder(fs):
    assert prepare_folder_target(
        src_name="filename.txt",
        dst="/some/original/folder/name.txt",
        autodetect_folder=True,
        simulate=False,
    ) == Path("/some/original/folder/name.txt")
    assert read_files("some") == {"original": {"folder": {}}}


# TODO: Hier ist das Ordnerhandling noch unklar, also wenn eine Resource
# ein Ordner ist.
