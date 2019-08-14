import textwrap

from .filter import Filter


class Python(Filter):
    def __init__(self, code):
        self.code = textwrap.dedent(code)
        if "return" not in self.code:
            raise ValueError("No return statement found in your code!")

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
        # this method is reassigned to user's code.
        raise NotImplementedError("No code given")

    def run(self, path):
        result = self.usercode(path)
        if result:
            return {"python": result}
