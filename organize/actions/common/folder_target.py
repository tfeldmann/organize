from pathlib import Path


def user_wants_a_folder(name: str, autodetect: bool) -> bool:
    return name.endswith("/") or (autodetect and "." not in name)


def prepare_folder_target(
    src_name: str,
    dst: str,
    autodetect_folder: bool,
    simulate: bool,
) -> Path:
    result = Path(dst)
    folder_wanted = user_wants_a_folder(dst, autodetect_folder)

    # check if dst is an existing folder
    if result.exists():
        if result.is_dir():
            return result / src_name
        elif folder_wanted:
            raise ValueError(f'Expected "{dst}" to be a folder, but it\'s not!')

    if not folder_wanted:
        return result

    if not simulate:
        result.mkdir(parents=True, exist_ok=True)
    return result / src_name
