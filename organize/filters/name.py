from schema import Or, Optional
from typing import Any, List, Union, Dict

import simplematch
from fs import path

from .filter import Filter, FilterResult


class Name(Filter):
    """Match files and folders by name

    Args:
        match (str):
            A matching string in [simplematch-syntax](https://github.com/tfeldmann/simplematch)

        startswith (str):
            The filename must begin with the given string

        contains (str):
            The filename must contain the given string

        endswith (str):
            The filename (without extension) must end with the given string

        case_sensitive (bool):
            By default, the matching is case sensitive. Change this to False to use
            case insensitive matching.
    """

    name = "name"
    schema_support_instance_without_args = True

    arg_schema = Or(
        str,
        {
            Optional("match"): str,
            Optional("startswith"): Or(str, [str]),
            Optional("contains"): Or(str, [str]),
            Optional("endswith"): Or(str, [str]),
            Optional("case_sensitive"): bool,
        },
    )

    def __init__(
        self,
        match="*",
        *,
        startswith="",
        contains="",
        endswith="",
        case_sensitive=True,
    ) -> None:
        self.matcher = simplematch.Matcher(match, case_sensitive=case_sensitive)
        self.startswith = self.create_list(startswith, case_sensitive)
        self.contains = self.create_list(contains, case_sensitive)
        self.endswith = self.create_list(endswith, case_sensitive)
        self.case_sensitive = case_sensitive

    def matches(self, name: str) -> bool:
        if not self.case_sensitive:
            name = name.lower()

        is_match = (
            self.matcher.test(name)
            and any(x in name for x in self.contains)
            and any(name.startswith(x) for x in self.startswith)
            and any(name.endswith(x) for x in self.endswith)
        )
        return is_match

    def pipeline(self, args: Dict) -> FilterResult:
        fs = args["fs"]
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            name = path.basename(fs_path)
        else:
            name, _ = path.splitext(path.basename(fs_path))
        result = self.matches(name)
        m = self.matcher.match(name)
        if m == {}:
            m = name
        return FilterResult(
            matches=result,
            updates={self.get_name(): m},
        )

    @staticmethod
    def create_list(x: Union[int, str, List[Any]], case_sensitive: bool) -> List[str]:
        if isinstance(x, (int, float)):
            x = str(x)
        if isinstance(x, str):
            x = [x]
        x = [str(x) for x in x]
        if not case_sensitive:
            x = [x.lower() for x in x]
        return x
