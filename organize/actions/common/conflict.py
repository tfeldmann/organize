from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from organize.actions.delete import Delete
from organize.actions.trash import Trash
from organize.output import Output
from organize.resource import Resource

if TYPE_CHECKING:
    from typing import Optional

    from jinja2 import Template


class ConflictMode(str, Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    TRASH = "trash"
    RENAME_NEW = "rename_new"
    RENAME_EXISTING = "rename_existing"
    # TODO: keep_newer
    # TODO: keep_older
    # TODO: keep_bigger
    # TODO: keep_smaller


def next_free_name(dst: Path, template: Template) -> Path:
    """
    Increments {counter} in the template until the given resource does not exist.

    Args:
        dst (Path):
            The destination path.
        template (jinja2.Template):
            A jinja2 template with placeholders for {name}, {extension} and {counter}

    Raises:
        ValueError if no free name can be found with the given template.

    Returns:
        (Path) A path according to the given template that does not exist.
    """
    if not dst.exists():
        return dst
    counter = 2
    prev_candidate = None
    while True:
        candidate = dst.with_name(
            template.render(
                name=dst.stem,
                extension=dst.suffix,
                counter=counter,
            )
        )
        if not candidate.exists():
            return candidate
        if prev_candidate == candidate:
            raise ValueError(
                "Could not find a free filename for the given template. "
                'Maybe you forgot the "{counter}" placeholder?'
            )
        prev_candidate = candidate
        counter += 1


class ConflictResult(NamedTuple):
    skip_action: bool
    use_dst: Optional[Path] = None


def resolve_conflict(
    dst: Path,
    res: Resource,
    conflict_mode: ConflictMode,
    rename_template: Template,
    simulate: bool,
    output: Output,
) -> ConflictResult:
    """
    Handle a conflict if `dst` already exists.
    """
    # no conflict, just continue with the action.
    if not dst.exists():
        return ConflictResult(skip_action=False, use_dst=dst)

    output.msg(
        res=res, msg=f'"{dst}" already exists! (Conflict mode is "{conflict_mode}")'
    )

    if res.path.resolve() == dst.resolve():
        output.msg(res=res, msg="Same resource: Skipped.", sender="conflict")
        return ConflictResult(skip_action=True, use_dst=res.path)

    if conflict_mode == ConflictMode.TRASH:
        Trash().pipeline(res=Resource(dst), output=output, simulate=simulate)
        return ConflictResult(skip_action=False, use_dst=dst)

    elif conflict_mode == ConflictMode.SKIP:
        output("Skipped.")
        return ConflictResult(skip_action=True, use_dst=res.path)

    elif conflict_mode == ConflictMode.OVERWRITE:
        output(f"Overwriting {dst}.")
        Delete().pipeline(res=Resource(dst), output=output, simulate=simulate)
        return ConflictResult(skip_action=False, use_dst=dst)

    elif conflict_mode == ConflictMode.RENAME_NEW:
        stem, ext = splitext(dst)
        name = next_free_name(
            fs=dst_fs,
            name=stem,
            extension=ext,
            template=rename_template,
        )
        return name

    elif conflict_mode == ConflictMode.RENAME_EXISTING:
        stem, ext = splitext(dst)
        name = next_free_name(
            fs=dst_fs,
            name=stem,
            extension=ext,
            template=rename_template,
        )
        output('Renaming existing to: "%s"' % name)
        if not simulate:
            if dst_fs.isdir(dst):
                move_dir(dst_fs, dst, dst_fs, name)
            elif dst_fs.isfile(dst):
                move_file(dst_fs, dst, dst_fs, name)
        return dst

    raise ValueError("Unknown conflict_mode %s" % conflict_mode)
