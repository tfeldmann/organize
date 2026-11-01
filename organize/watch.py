"""
Runs a config whenever files are added to one of its locations.

After a change the watcher waits until the folder has been quiet for `delay`
seconds, so files that are still being downloaded or copied are not touched.
Changes inside subfolders count as well, so a folder that is still being filled
(e.g. while a zip file is extracted) is not moved halfway.
"""

import threading
import time
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Set

from organize.config import Config
from organize.logger import logger
from organize.template import render

DEFAULT_DELAY = 5.0


def watched_folders(config: Config) -> List[Path]:
    """The existing folders of all rule locations."""
    result: Set[Path] = set()
    for rule in config.rules:
        for location in rule.locations:
            for path in location.path:
                folder = Path(render(path))
                if folder.is_dir():
                    result.add(folder.resolve())
    return sorted(result)


class Debouncer:
    """Calls `action` once no event arrived for `delay` seconds."""

    def __init__(
        self,
        delay: float,
        action: Callable[[], None],
        clock: Callable[[], float] = time.monotonic,
    ):
        self.delay = delay
        self.action = action
        self.clock = clock
        self._last_event: Optional[float] = None
        self._lock = threading.Lock()

    def event(self) -> None:
        with self._lock:
            self._last_event = self.clock()

    def poll(self) -> bool:
        """Runs the action if it is due. Returns whether it ran."""
        with self._lock:
            due = (
                self._last_event is not None
                and self.clock() - self._last_event >= self.delay
            )
            if due:
                self._last_event = None
        if due:
            self.action()
        return due


def is_relevant(path: str, folders: Iterable[Path]) -> bool:
    """Whether an event at `path` is a change of something inside a folder."""
    p = Path(path)
    for folder in folders:
        try:
            rel = p.relative_to(folder)
        except ValueError:
            continue
        # ignore hidden files like .DS_Store and changes to the folder itself
        return bool(rel.parts) and not any(x.startswith(".") for x in rel.parts)
    return False


def watch(
    load_config: Callable[[], Config],
    run: Callable[[Config], None],
    delay: float = DEFAULT_DELAY,
    stop: Optional[threading.Event] = None,
) -> None:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    stop = stop or threading.Event()
    config = load_config()
    folders = watched_folders(config)
    if not folders:
        raise ValueError("None of the config locations exist, nothing to watch.")

    def run_config():
        nonlocal config
        try:
            config = load_config()  # pick up changes to the config file
        except Exception as e:
            logger.exception(e)
            print(f"Config error, using the previous config: {e}")
        run(config)

    debouncer = Debouncer(delay=delay, action=run_config)

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            if event.event_type not in (
                "created",
                "modified",
                "moved",
                "closed",
            ):
                return
            # for moves only the destination matters (a file moved in)
            path = getattr(event, "dest_path", "") or event.src_path
            if is_relevant(str(path), folders):
                debouncer.event()

    observer = Observer()
    for folder in folders:
        observer.schedule(Handler(), str(folder), recursive=True)
    observer.start()
    print(f"Watching {', '.join(str(f) for f in folders)} (delay {delay:g}s)")
    try:
        run(config)  # sort what is already there
        while not stop.is_set():
            debouncer.poll()
            stop.wait(0.2)
    finally:
        observer.stop()
        observer.join()
