from functools import partial
from typing import Optional, Tuple, Union

from fs.base import FS

from .config import Config, load_from_string


def execute(
    config: Union[Config, dict, str],
    simulate: bool,
    working_dir: Union[FS, str],
    tags: Optional[Tuple[str]] = None,
    skip_tags: Optional[Tuple[str]] = None,
):
    if isinstance(config, str):
        config = load_from_string(str)
    if isinstance(config, dict):
        config = Config.parse_obj(config)

    config.execute(
        working_dir=working_dir,
        simulate=simulate,
        tags=tags,
        skip_tags=skip_tags,
    )


run = partial(execute, simulate=False)
sim = partial(execute, simulate=True)
