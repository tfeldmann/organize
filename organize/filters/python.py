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

    def create_method(self, name, argnames, code):
        globals_ = globals().copy()
        globals_["print"] = self.print
        locals_ = locals().copy()
        locals_["self"] = self
        funccode = "def {fnc}__({arg}):\n{cod}\n\nself.{fnc} = {fnc}__\n".format(
            fnc=name,
            arg=", ".join(argnames),
            cod=textwrap.indent(textwrap.dedent(code), " " * 4),
        )
        exec(funccode, globals_, locals_)  # pylint: disable=exec-used

    def pipeline(self, args):
        self.create_method(name="usercode", argnames=args.keys(), code=self.code)
        result = self.usercode(**args)  # pylint: disable=no-member
        if result not in (False, None):
            return {"python": result}
