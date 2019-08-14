import operator
import re

from organize.utils import flattened_string_list, fullpath

from .filter import Filter

OPERATORS = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "=": operator.eq,
    "": operator.eq,
    ">=": operator.ge,
    ">": operator.gt,
}
SIZE_REGEX = re.compile(
    r"^(?P<op>[<>=]*)(?P<num>(\d*\.)?\d+)(?P<unit>[kmgtpezy]?i?)b?$"
)


def create_constrains(inp):
    """
    Given an input string it returns a list of tuples (comparison operator,
    number of bytes).

    Accepted formats are: '30k', '>= 5 TiB, <10tb', '< 60 tb', ...
    Calculation is in bytes, even if the 'b' is lowercase. If an 'i' is present
    we calculate base 1024.
    """
    result = set()
    parts = inp.replace(" ", "").lower().split(",")
    for part in parts:
        try:
            match = SIZE_REGEX.match(part).groupdict()
            op = OPERATORS[match["op"]]
            num = float(match["num"]) if "." in match["num"] else int(match["num"])
            unit = match["unit"]
            base = 1024 if unit.endswith("i") else 1000
            exp = "kmgtpezy".index(unit[0]) + 1 if unit else 0
            numbytes = num * base ** exp
            result.add((op, numbytes))
        except (AttributeError, KeyError, IndexError, ValueError, TypeError) as e:
            raise ValueError("Invalid size format: %s" % part) from e
    return result


def satisfies_constrains(size, constrains):
    return all(op(size, p_size) for op, p_size in constrains)


class FileSize(Filter):
    """
    Matches files by file size

    :param str conditions:

    Accepts file size conditions, e.g: ``'>= 500 MB'``, ``'< 20k'``, ``'>0'``,
    ``'= 10 KiB'``.

    It is possible to define both lower and upper conditions like this:
    ``'>20k, < 1 TB'``, ``'>= 20 Mb, <25 Mb'``. The filter will match if all given
    conditions are satisfied.

    - Accepts all units from KB to YB.
    - If no unit is given, kilobytes are assumend.
    - If binary prefix is given (KiB, GiB) the size is calculated using base 1024.

    :returns:
        - ``{filesize.bytes}`` -- File size in bytes

    Examples:
        - Trash big downloads:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Downloads'
                filters:
                  - filesize: '> 500 MB'
                actions:
                  - trash

    """

    def __init__(self, *conditions):
        self.conditions = ", ".join(flattened_string_list(list(conditions)))
        self.constrains = create_constrains(self.conditions)
        if not self.constrains:
            raise ValueError("No size(s) given!")

    def matches(self, filesize):
        return all(op(filesize, c_size) for op, c_size in self.constrains)

    def run(self, path):
        file_size = fullpath(path).stat().st_size
        if self.matches(file_size):
            return {"filesize": {"bytes": file_size}}

    def __str__(self):
        return "FileSize({})".format(" ".join(self.conditions))
