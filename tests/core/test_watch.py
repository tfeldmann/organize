import threading
import time
from pathlib import Path

from organize import Config
from organize.watch import Debouncer, is_relevant, watch, watched_folders


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_debouncer_waits_for_quiet():
    clock = Clock()
    calls = []
    deb = Debouncer(delay=5, action=lambda: calls.append(clock.now), clock=clock)

    assert not deb.poll()  # no event yet
    deb.event()
    clock.now = 3
    deb.event()  # a second file restarts the delay
    clock.now = 7
    assert not deb.poll()
    clock.now = 8
    assert deb.poll()
    assert calls == [8]
    clock.now = 20
    assert not deb.poll()  # runs only once per batch


def test_is_relevant():
    folders = [Path("/home/Downloads")]
    assert is_relevant("/home/Downloads/a.pdf", folders)
    assert not is_relevant("/home/Downloads/.hidden", folders)
    assert is_relevant("/home/Downloads/New Folder", folders)
    assert is_relevant("/home/Downloads/project/still-copying.bin", folders)
    assert not is_relevant("/home/Downloads/project/.git/index", folders)
    assert not is_relevant("/home/Downloads", folders)
    assert not is_relevant("/elsewhere/a.pdf", folders)


def test_watched_folders(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    config = Config.from_string(
        f"""
        rules:
          - locations: ["{tmp_path}/a", "{tmp_path}/b", "{tmp_path}/missing"]
            actions:
              - echo: "x"
          - locations: "{tmp_path}/a"
            actions:
              - echo: "x"
        """
    )
    assert watched_folders(config) == [
        (tmp_path / "a").resolve(),
        (tmp_path / "b").resolve(),
    ]


def test_watch_runs_after_new_file(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    config = Config.from_string(
        f"""
        rules:
          - locations: "{inbox}"
            actions:
              - echo: "x"
        """
    )
    runs = []
    stop = threading.Event()
    thread = threading.Thread(
        target=watch,
        kwargs=dict(
            load_config=lambda: config,
            run=lambda conf: runs.append(time.monotonic()),
            delay=0.5,
            stop=stop,
        ),
    )
    thread.start()
    try:
        _wait_for(lambda: len(runs) == 1)  # the initial run
        time.sleep(0.5)
        (inbox / "new.txt").write_text("hello")
        _wait_for(lambda: len(runs) == 2, timeout=10)
    finally:
        stop.set()
        thread.join(timeout=5)
    assert len(runs) == 2


def _wait_for(condition, timeout=5.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if condition():
            return
        time.sleep(0.05)
    raise AssertionError("Timed out")


def test_watch_runs_after_new_folder(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    config = Config.from_string(
        f"""
        rules:
          - locations: "{inbox}"
            targets: dirs
            actions:
              - echo: "x"
        """
    )
    runs = []
    stop = threading.Event()
    thread = threading.Thread(
        target=watch,
        kwargs=dict(
            load_config=lambda: config,
            run=lambda conf: runs.append(time.monotonic()),
            delay=0.5,
            stop=stop,
        ),
    )
    thread.start()
    try:
        _wait_for(lambda: len(runs) == 1)
        time.sleep(0.5)
        (inbox / "unpacked").mkdir()
        _wait_for(lambda: len(runs) == 2, timeout=10)
    finally:
        stop.set()
        thread.join(timeout=5)
