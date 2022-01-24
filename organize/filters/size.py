import operator
import re
from typing import Callable, Dict
from typing import Optional as Opt
from typing import Sequence, Set, Tuple

from fs.filesize import binary, decimal, traditional
from schema import Optional, Or

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


def create_constraints(inp: str) -> Set[Tuple[Callable[[int, int], bool], int]]:
    """
    Given an input string it returns a list of tuples (comparison operator,
    number of bytes).

    Accepted formats are: '30k', '>= 5 TiB, <10tb', '< 60 tb', ...
    Calculation is in bytes, even if the 'b' is lowercase. If an 'i' is present
    we calculate base 1024.
    """
    result = set()  # type: Set[Tuple[Callable[[int, int], bool], int]]
    parts = str(inp).replace(" ", "").lower().split(",")
    for part in parts:
        try:
            reg_match = SIZE_REGEX.match(part)
            if reg_match:
                match = reg_match.groupdict()
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


def satisfies_constraints(size, constraints):
    return all(op(size, p_size) for op, p_size in constraints)


class Size(Filter):
    """
    Matches files and folders by size

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
        - ``{size.bytes}`` -- Size in bytes

    Examples:
        - Trash big downloads:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - locations: '~/Downloads'
                targets: files
                filters:
                  - filesize: '> 0.5 GB'
                actions:
                  - trash

        - Move all JPEGS bigger > 1MB and <10 MB. Search all subfolders and keep the
          original relative path.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Pictures'
                subfolders: true
                filters:
                  - extension:
                      - jpg
                      - jpeg
                  - filesize: '>1mb, <10mb'
                actions:
                  - move: '~/Pictures/sorted/{relative_path}/'

    """

    name = "size"
    arg_schema = Optional(Or(str, [str], int, [int]))
    schema_support_instance_without_args = True

    def __init__(self, *conditions: Sequence[str]) -> None:
        self.conditions = ", ".join(flattened_string_list(list(conditions)))
        self.constraints = create_constraints(self.conditions)

    def matches(self, filesize: int) -> bool:
        if not self.constraints:
            return True
        return all(op(filesize, c_size) for op, c_size in self.constraints)

    def pipeline(self, args: dict) -> Opt[Dict[str, Dict[str, int]]]:
        fs = args["fs"]
        fs_path = args["fs_path"]

        if fs.isdir(fs_path):
            size = sum(
                info.size
                for _, info in fs.walk.info(path=fs_path, namespaces=["details"])
            )
        else:
            size = fs.getinfo(fs_path, namespaces=["details"]).size
        if self.matches(size):
            return {
                self.name: {
                    "bytes": size,
                    "traditional": traditional(size),
                    "binary": binary(size),
                    "decimal": decimal(size),
                },
            }
        return None

    def __str__(self) -> str:
        return "FileSize({})".format(" ".join(self.conditions))
