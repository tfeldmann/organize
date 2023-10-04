from pathlib import Path


def user_wants_a_folder(path: str, autodetect: bool) -> bool:
    """
    Try to detect whether the user meant a folder target
    """
    if path.endswith(("/", "\\")):
        return True

    if autodetect:
        return "." not in Path(path).name

    return False


def prepare_target_path(
    src_name: str,
    dst: str,
    autodetect_folder: bool,
    simulate: bool,
) -> Path:
    result = Path(dst)
    wants_folder = user_wants_a_folder(path=dst, autodetect=autodetect_folder)

    # if dst is an existing folder, we use it
    if result.exists():
        if result.is_dir():
            return result / src_name
        elif wants_folder:
            raise ValueError(f'Expected "{dst}" to be a folder, but it\'s not!')

    if wants_folder:
        if not simulate:
            result.mkdir(parents=True, exist_ok=True)
        return result / src_name
    else:
        if not simulate:
            result.parent.mkdir(parents=True, exist_ok=True)
        return result
