import textwrap

from organize.utils import DotDict, flatten

from .filter import Filter


class Python(Filter):
    def __init__(self, code):
        self.code = textwrap.dedent(code)
        if "return" not in self.code:
            raise Exception("No return statement found in your code!")

        # bind usercode to class as new method
        method = (
            "def _usercode(path):\n"
            + textwrap.indent(self.code, "    ")
            + "\n\n"
            + "self.usercode = _usercode"
        )
        globals_ = globals().copy()
        globals_["print"] = self.print
        exec(method, globals_, {"self": self})

    def usercode(self, path):
        raise NotImplementedError("No code given")

    def matches(self, path):
        return self.usercode(path)

    def parse(self, path):
        result = DotDict(self.usercode(path))
        return {"python": result}
