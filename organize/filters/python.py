import textwrap
from typing import ClassVar, Dict, Optional

from pydantic import field_validator
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Python:
    """Use python code to filter files.

    Attributes:
        code (str):
            The python code to execute. The code must contain a `return` statement.


    **Returns:**

    - If your code returns `False` or `None` the file is filtered out,
      otherwise the file is passed on to the next filters.
    - `{python}` contains the returned value. If you return a dictionary (for
      example `return {"some_key": some_value, "nested": {"k": 2}}`) it will be
      accessible via dot syntax actions: `{python.some_key}`, `{python.nested.k}`.
    - Variables of previous filters are available, but you have to use the normal python
      dictionary syntax `x = regex["my_group"]`.
    """

    code: str

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="python",
        files=True,
        dirs=True,
    )

    @field_validator("code", mode="after")
    @classmethod
    def must_have_return_statement(cls, value):
        if "return" not in value:
            raise ValueError("No return statement found in your code!")
        return value

    def __post_init__(self):
        self.code = textwrap.dedent(self.code)

    def __usercode__(self, print, **kwargs) -> Optional[Dict]:
        raise NotImplementedError()

    def pipeline(self, res: Resource, output: Output) -> bool:
        def _output_msg(*values, sep: str = " ", end: str = ""):
            """
            the print function for the use code needs to print via the current output
            """
            output.msg(
                res=res,
                msg=f"{sep.join(str(x) for x in values)}{end}",
                sender="python",
            )

        # codegen the user function with arguments as available in the resource
        kwargs = ", ".join(res.dict().keys())
        func = f"def __userfunc(print, {kwargs}):\n"
        func += textwrap.indent(self.code, "    ")
        func += "\n\nself.__usercode__ = __userfunc"

        exec(func, globals().copy(), locals().copy())
        result = self.__usercode__(print=_output_msg, **res.dict())

        if isinstance(result, dict):
            res.deep_merge(key=self.filter_config.name, data=result)
        else:
            res.vars[self.filter_config.name] = result
        return result not in (False, None)
