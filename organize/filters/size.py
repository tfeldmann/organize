import operator
import re
from typing import Callable, ClassVar, Iterable, List, Set, Tuple, Union

from pydantic import validator
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.utils import flattened_string_list

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

    Accepted formats are: "30k", ">= 5 TiB, <10tb", "< 60 tb", ...
    Calculation is in bytes, even if the "b" is lowercase. If an "i" is present
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
                numbytes = num * base**exp
                result.add((op, numbytes))
        except (AttributeError, KeyError, IndexError, ValueError, TypeError) as e:
            raise ValueError("Invalid size format: %s" % part) from e
    return result


def satisfies_constraints(size, constraints):
    return all(op(size, p_size) for op, p_size in constraints)


def number_with_unit(size: int, suffixes: Iterable[str], base: int) -> str:
    size = int(size)
    if size == 1:
        return "1 byte"
    elif size < base:
        return "{:,} bytes".format(size)

    for i, suffix in enumerate(suffixes, 2):
        unit = base**i
        if size < unit:
            break
    return "{:,.1f} {}".format((base * size / unit), suffix)


def traditional(size):
    """Convert a filesize in to a string (powers of 1024, JDEC prefixes)."""
    return number_with_unit(
        size, ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"), 1024
    )


def binary(size):
    """Convert a filesize in to a string (powers of 1024, IEC prefixes)."""
    return number_with_unit(
        size, ("KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"), 1024
    )


def decimal(size):
    """Convert a filesize in to a string (powers of 1000, SI prefixes)."""
    return number_with_unit(
        size, ("kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"), 1000
    )


@dataclass
class Size:
    """Matches files and folders by size

    Args:
        *conditions (list(str) or str):
            The size constraints.

    Accepts file size conditions, e.g: `">= 500 MB"`, `"< 20k"`, `">0"`,
    `"= 10 KiB"`.

    It is possible to define both lower and upper conditions like this:
    `">20k, < 1 TB"`, `">= 20 Mb, <25 Mb"`. The filter will match if all given
    conditions are satisfied.

    - Accepts all units from KB to YB.
    - If no unit is given, kilobytes are assumend.
    - If binary prefix is given (KiB, GiB) the size is calculated using base 1024.

    **Returns:**

    - `{size.bytes}`: (int) Size in bytes
    - `{size.traditional}`: (str) Size with unit (powers of 1024, JDEC prefixes)
    - `{size.binary}`: (str) Size with unit (powers of 1024, IEC prefixes)
    - `{size.decimal}`: (str) Size with unit (powers of 1000, SI prefixes)
    """

    conditions: Union[List[str], str] = ""

    filter_config: ClassVar = FilterConfig(name="size", files=True, dirs=True)

    @validator("conditions", pre=True)
    def ensure_joined_str(cls, value):
        if isinstance(value, str):
            value = [value]
        return ", ".join(flattened_string_list(list(value)))

    def __post_init__(self):
        self._constraints = create_constraints(self.conditions)

    def matches(self, filesize: int) -> bool:
        if not self._constraints:
            return True
        return all(op(filesize, c_size) for op, c_size in self._constraints)

    def pipeline(self, res: Resource, output: Output) -> bool:
        bytes = res.size()
        res.vars[self.filter_config.name] = {
            "bytes": bytes,
            "traditional": traditional(bytes),
            "binary": binary(bytes),
            "decimal": decimal(bytes),
        }
        return self.matches(bytes)
