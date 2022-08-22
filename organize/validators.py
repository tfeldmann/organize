from pydantic import validator


def convert_to_list(cls, v):
    if not v:
        return []
    if isinstance(v, str):
        return v.split()
    return v


def ensure_list(field_name: str):
    return validator(field_name, allow_reuse=True, pre=True)(convert_to_list)
