from pathlib import Path

from organize.actions.common.folder_target import (
    prepare_folder_target,
    user_wants_a_folder,
)


def test_user_wants_a_folder():
    assert user_wants_a_folder("/test/", autodetect=False)
    assert not user_wants_a_folder("/test", autodetect=False)
    assert not user_wants_a_folder("/test.asd", autodetect=False)
    assert user_wants_a_folder("/test.asd/", autodetect=False)


def test_user_wants_a_folder_autodetect():
    assert user_wants_a_folder("/test/", autodetect=True)
    assert user_wants_a_folder("/test", autodetect=True)
    assert not user_wants_a_folder("/test.asd", autodetect=True)
    assert user_wants_a_folder("/test.asd/", autodetect=True)


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
    assert Path("/test").exists()


def test_prepare_folder_target_advanced(fs):
    assert prepare_folder_target(
        src_name="dst",
        dst="/some/test/folder",
        autodetect_folder=True,
        simulate=False,
    ) == Path("/some/test/folder/dst")
    assert Path("/some/test/folder").exists()
    assert not Path("/some/test/folder/dst").exists()


def test_prepare_folder_target_already_exists(fs):
    Path("/some/Application.app").mkdir(parents=True)
    assert prepare_folder_target(
        src_name="info.plist",
        dst="/some/Application.app",
        autodetect_folder=True,
        simulate=False,
    ) == Path("/some/Application.app/info.plist")
