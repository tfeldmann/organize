from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

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


class ConflictResult(NamedTuple):
    skip_action: bool  # Whether to skip the current action
    use_dst: Path  # The Path to continue with


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
        new_name = template.render(
            name=dst.stem,
            extension=dst.suffix,
            counter=counter,
        )
        candidate = dst.with_name(new_name)
        if not candidate.exists():
            return candidate
        if prev_candidate == candidate:
            raise ValueError(
                "Could not find a free filename for the given template. "
                'Maybe you forgot the "{counter}" placeholder?'
            )
        prev_candidate = candidate
        counter += 1


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
    assert res.path is not None

    # no conflict, just continue with the action.
    if not dst.exists():
        return ConflictResult(skip_action=False, use_dst=dst)

    def _print(msg: str):
        output.msg(res=res, sender="conflict", msg=msg)

    _print(f'"{dst}" already exists! (Conflict mode is "{conflict_mode}")')

    if res.path.resolve() == dst.resolve():
        _print("Same resource: Skipped.")
        return ConflictResult(skip_action=True, use_dst=res.path)

    if conflict_mode == ConflictMode.TRASH:
        _print(f'Trash "{dst}"')
        if not simulate:
            from organize.actions.trash import trash

            trash(path=dst)
        return ConflictResult(skip_action=False, use_dst=dst)

    elif conflict_mode == ConflictMode.SKIP:
        _print("Skipped.")
        return ConflictResult(skip_action=True, use_dst=res.path)

    elif conflict_mode == ConflictMode.OVERWRITE:
        _print(f"Overwriting {dst}.")
        if not simulate:
            from organize.actions.delete import delete

            delete(path=dst)
        return ConflictResult(skip_action=False, use_dst=dst)

    elif conflict_mode == ConflictMode.RENAME_NEW:
        new_path = next_free_name(
            dst=dst,
            template=rename_template,
        )
        return ConflictResult(skip_action=False, use_dst=new_path)

    elif conflict_mode == ConflictMode.RENAME_EXISTING:
        new_path = next_free_name(
            dst=dst,
            template=rename_template,
        )
        _print('Renaming existing to: "{new_path.name}"')
        if not simulate:
            dst.rename(new_path)
        return ConflictResult(skip_action=False, use_dst=dst)

    raise ValueError("Unknown conflict_mode %s" % conflict_mode)
