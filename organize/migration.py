class MigrationWarning(UserWarning):
    pass


class NeedsMigrationError(Exception):
    pass


def entry_name_args(entry):
    if isinstance(entry, str):
        return (entry.lower(), [])
    elif isinstance(entry, dict):
        name, value = next(iter(entry.items()))
        if isinstance(value, str):
            return (name.lower(), [])
        elif isinstance(value, dict):
            args = [x.lower() for x in value.keys()]
            return (name.lower(), args)
        return (name.lower(), [])


def migrate_v1(config: dict):
    for rule in config.get("rules") or []:
        if "folders" in rule:
            raise NeedsMigrationError("`folders` are now `locations`")
        for fil in rule.get("filters") or []:
            name, _ = entry_name_args(fil)
            if name == "filename":
                raise NeedsMigrationError("`filename` is now `name`")
            if name == "filesize":
                raise NeedsMigrationError("`filesize` is now `size`")
        for act in rule.get("actions") or []:
            if act:
                name, args = entry_name_args(act)
                if name in ("move", "copy", "rename"):
                    if "overwrite" in args or "counter_seperator" in args:
                        raise NeedsMigrationError(
                            "`%s` does not support `overwrite` and "
                            "`counter_seperator` anymore. Please use the new arguments."
                        )
