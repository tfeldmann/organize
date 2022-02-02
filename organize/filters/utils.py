from datetime import datetime, timedelta


def age_condition_applies(dt: datetime, age: timedelta, mode: str, reference: datetime):
    """
    Returns whether `dt` is older / newer (`mode`) than `age` as measured on `reference`
    """
    if mode not in ("older", "newer"):
        raise ValueError(mode)

    is_past = (dt + age).timestamp() < reference.timestamp()
    return (mode == "older") == is_past
