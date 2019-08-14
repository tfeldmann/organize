import textwrap

from .filter import Filter
from organize.utils import DotDict


class Python(Filter):

    r"""
    Use python code to filter files.

    :param str code: The python code to execute
    """

    def __init__(self, code):
        self.code = textwrap.dedent(code)
        if "return" not in self.code:
            raise ValueError("No return statement found in your code!")

        # the user's code becomes a method of the filter instance
        self.method = (
            "def _usercode(attrs):\n"
            + textwrap.indent(self.code, "    ")
            + "\n"
            + "self.usercode = _usercode"
        )
        globals_ = globals().copy()
        globals_["print"] = self.print
        exec(self.method, globals_, {"self": self})

    def usercode(self, attrs):
        raise NotImplementedError("No user code given")

    def run(self, attrs):
        result = self.usercode(attrs)
        if result:
            return {"python": result}
