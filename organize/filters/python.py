import textwrap
from typing import Any, Dict, Optional, Sequence

from .filter import Filter


class Python(Filter):

    r"""
    Use python code to filter files.

    :param str code:
        The python code to execute. The code must contain a ``return`` statement.


    :returns:
        - If your code returns ``False`` or ``None`` the file is filtered out,
          otherwise the file is passed on to the next filters.
        - ``{python}`` contains the returned value. If you return a dictionary (for
          example ``return {"some_key": some_value, "nested": {"k": 2}}``) it will be
          accessible via dot syntax in your actions: ``{python.some_key}``,
          ``{python.nested.k}``.
    """

    name = "python"

    def __init__(self, code) -> None:
        self.code = textwrap.dedent(code)
        if "return" not in self.code:
            raise ValueError("No return statement found in your code!")

    def usercode(self, *args, **kwargs) -> Optional[Any]:
        pass  # will be overwritten by `create_method`

    def create_method(self, name: str, argnames: Sequence[str], code: str) -> None:
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

    def pipeline(self, args) -> Optional[Dict[str, Any]]:
        self.create_method(name="usercode", argnames=args.keys(), code=self.code)
        result = self.usercode(**args)  # pylint: disable=assignment-from-no-return
        if result not in (False, None):
            return {"python": result}
        return None
