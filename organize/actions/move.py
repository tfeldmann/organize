import shutil
from pathlib import Path
from typing import ClassVar

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.utils import Template

# from .common.conflict import ConflictOption


@dataclass
class Move:

    """Move a file to a new location.

    The file can also be renamed.
    If the specified path does not exist it will be created.

    If you only want to rename the file and keep the folder, it is
    easier to use the `rename` action.

    Args:
        dest (str):
            The destination where the file / dir should be moved to.
            If `dest` ends with a slash, it is assumed to be a target directory
            and the file / dir will be moved into `dest` and keep its name.

        on_conflict (str):
            What should happen in case **dest** already exists.
            One of `skip`, `overwrite`, `trash`, `rename_new` and `rename_existing`.
            Defaults to `rename_new`.

        rename_template (str):
            A template for renaming the file / dir in case of a conflict.
            Defaults to `{name} {counter}{extension}`.

    The next action will work with the moved file / dir.
    """

    dest: str
    # on_conflict: ConflictOption = ConflictOption.rename_new
    rename_template: str = "{name} {counter}{extension}"

    action_config: ClassVar = ActionConfig(
        name="move",
        standalone=False,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._dest = Template.from_string(self.dest)
        self._rename_template = Template.from_string(self.rename_template)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        dst = Path(self._dest.render(**res.dict()))
        if not simulate:
            output.msg(res=res, msg=f"Move to {dst}", sender=self)
            shutil.move(src=res.path, dst=dst)
        res.path = dst

        # # check for conflicts
        # skip, dst_path = check_conflict(
        #     src=res.path,
        #     dest=dest,
        #     conflict_mode=self.on_conflict,
        #     rename_template=self._rename_template,
        #     simulate=simulate,
        #     output=output,
        # )

        # # use move_dir or move_file depending on src resource type
        # move_action: Callable[[FS, str, FS, str], None]
        # if res.path.is_dir():
        #     move_action = partial(fs.move.move_dir, preserve_time=True)
        # elif res.path.is_file():
        #     move_action = partial(fs.move.move_file, preserve_time=True)

        # try:
        #     dst_fs = fs.open_fs(dst_fs, create=False, writeable=True)
        # except (fs.errors.CreateFailed, OpenerError):
        #     if not simulate:
        #         dst_fs = fs.open_fs(dst_fs, create=True, writeable=True)
        #     else:
        #         dst_fs = SimulationFS(dst_fs)

        # if not skip:
        #     self.print("Move to %s" % safe_description(dst_fs, dst_path))
        #     if not simulate:
        #         dst_fs.makedirs(fs.path.dirname(dst_path), recreate=True)
        #         move_action(src_fs, src_path, dst_fs, dst_path)
