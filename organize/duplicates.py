"""
Marking files as duplicates of files that already exist.

A marked file gets the Finder tag "Duplicate" (on macOS) and the path of its
original in an extended attribute (an alternate data stream on Windows), which
stays with the file when it is moved.
"""

import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

TAG = "Duplicate"
ORIGINAL_ATTR = "local.organize.duplicate-of"


def _set_attr(path: Path, value: str) -> None:
    if sys.platform == "win32":
        # NTFS alternate data stream, kept when the file is moved
        with open(f"{path}:{ORIGINAL_ATTR}", "w", encoding="utf-8") as f:
            f.write(value)
    else:
        import xattr

        xattr.setxattr(str(path), ORIGINAL_ATTR, value.encode("utf-8"))


def _get_attr(path: Path) -> Optional[str]:
    try:
        if sys.platform == "win32":
            with open(f"{path}:{ORIGINAL_ATTR}", encoding="utf-8") as f:
                return f.read()
        import xattr

        return xattr.getxattr(str(path), ORIGINAL_ATTR).decode("utf-8")
    except OSError:
        return None


def _remove_attr(path: Path) -> None:
    try:
        if sys.platform == "win32":
            os.remove(f"{path}:{ORIGINAL_ATTR}")
        else:
            import xattr

            xattr.removexattr(str(path), ORIGINAL_ATTR)
    except OSError:
        pass


def mark(
    path: Path, original: Path, tag: Optional[str] = TAG, color: str = "red"
) -> None:
    _set_attr(path, str(original))
    if tag and sys.platform == "darwin":
        import macos_tags

        macos_tags.add(
            macos_tags.Tag(name=tag, color=macos_tags.Color[color.upper()]),  # type: ignore
            file=str(path),
        )


def unmark(path: Path, tag: Optional[str] = TAG) -> None:
    _remove_attr(path)
    if tag and sys.platform == "darwin":
        import macos_tags

        for t in macos_tags.get_all(str(path)):
            if t.name == tag:
                macos_tags.remove(t, file=str(path))


def original_of(path: Path) -> Optional[Path]:
    value = _get_attr(path)
    return Path(value) if value is not None else None


def walk_files(folder: Path) -> Iterator[Path]:
    """All files below `folder`, skipping hidden files and folders."""
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            if not name.startswith("."):
                yield Path(root) / name


def find_marked(folders: List[Path]) -> List[Dict[str, Any]]:
    """
    The marked duplicates below `folders` and their originals. If an original was
    moved since, it is looked up by its content.
    """
    marked = []
    for folder in folders:
        for path in walk_files(folder):
            original = original_of(path)
            if original is not None:
                marked.append((path, original))

    by_size: Optional[Dict[int, List[Path]]] = None
    result = []
    for path, original in marked:
        if not original.exists():
            if by_size is None:
                by_size = _files_by_size(folders)
            original = _find_by_content(path, by_size) or original
        result.append(
            {
                "path": str(path),
                "original": str(original),
                "original_exists": original.exists(),
            }
        )
    return result


def _files_by_size(folders: List[Path]) -> Dict[int, List[Path]]:
    result: Dict[int, List[Path]] = defaultdict(list)
    for folder in folders:
        for path in walk_files(folder):
            try:
                result[path.stat().st_size].append(path)
            except OSError:
                pass
    return result


def _find_by_content(path: Path, by_size: Dict[int, List[Path]]) -> Optional[Path]:
    from organize.filters.hash import hash

    size = path.stat().st_size
    wanted = None
    for candidate in by_size.get(size, []):
        if candidate == path or original_of(candidate) is not None:
            continue  # other duplicates are not the original
        wanted = wanted or hash(path, algo="sha256")
        if hash(candidate, algo="sha256") == wanted:
            return candidate
    return None


def _created(path: Path) -> float:
    st = path.stat()
    return getattr(st, "st_birthtime", st.st_mtime)


def find_existing(paths: List[Path]) -> List[Dict[str, str]]:
    """
    Groups identical files among `paths`. In each group the oldest file is the
    original, the others are returned as duplicates (unless already marked).
    """
    from organize.filters.hash import hash

    by_size: Dict[int, List[Path]] = defaultdict(list)
    for path in set(paths):
        if path.is_file() and not path.is_symlink():
            size = path.stat().st_size
            if size > 0:
                by_size[size].append(path)

    result = []
    for group in by_size.values():
        if len(group) < 2:
            continue
        by_hash: Dict[str, List[Path]] = defaultdict(list)
        for path in group:
            by_hash[hash(path, algo="sha256")].append(path)
        for same in by_hash.values():
            if len(same) < 2:
                continue
            original, *copies = sorted(same, key=lambda p: (_created(p), str(p)))
            for copy in copies:
                if original_of(copy) is None:
                    result.append({"path": str(copy), "original": str(original)})
    return sorted(result, key=lambda x: x["path"])


def sorted_files(folders: List[Path]) -> List[Path]:
    """
    The loose files below `folders` that organize has sorted (according to the
    history) - but not the content of folders that were moved as a whole.
    """
    from organize import history

    resolved = [f.resolve() for f in folders]
    result = []
    for run in history.runs():
        if run.undone:
            continue
        for op in run.ops:
            if op["op"] not in ("move", "rename"):
                continue
            dst = Path(op["dst"])
            if dst.is_file() and any(f in dst.parents for f in resolved):
                result.append(dst)
    return result
