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

    Examples:
      - A file name reverser.

        .. code-block:: yaml
            :caption: config.yaml

            rules:
            - folders: ~/Documents
              filters:
              - extension
              - python: |
                  return {"reversed_name": path.stem[::-1]}
              actions:
              - rename: '{python.reversed_name}.{extension}'

      - A filter for odd student numbers. Assuming the folder ``~/Students`` contains
        the files ``student-01.jpg``, ``student-01.txt``, ``student-02.txt`` and
        ``student-03.txt`` this rule will print
        ``"Odd student numbers: student-01.txt"`` and
        ``"Odd student numbers: student-03.txt"``

        .. code-block:: yaml
            :caption: config.yaml

            rules:
            - folders: ~/Students/
              filters:
               - python: |
                 return int(path.stem.split('-')[1]) % 2 == 1
               actions:
               - echo: 'Odd student numbers: {path.name}'


      - Advanced usecase. You can access data from previous filters in your python code.
        This can be used to match files and capturing names with a regular expression
        and then renaming the files with the output of your python script.

        .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: files
                filters:
                  - extension: txt
                  - regex: (?P<firstname>\w+)-(?P<lastname>\w+)\..*
                  - python: |
                      emails = {
                          "Betts": "dbetts@mail.de",
                          "Cornish": "acornish@google.com",
                          "Bean": "dbean@aol.com",
                          "Frey": "l-frey@frey.org",
                      }
                      if regex.lastname in emails: # get emails from wherever
                          return {"mail": emails[regex.lastname]}
                actions:
                  - rename: '{python.mail}.txt'

        Result:
         - ``Devonte-Betts.txt`` becomes ``dbetts@mail.de.txt``
         - ``Alaina-Cornish.txt`` becomes ``acornish@google.com.txt``
         - ``Dimitri-Bean.txt`` becomes ``dbean@aol.com.txt``
         - ``Lowri-Frey.txt`` becomes ``l-frey@frey.org.txt``
         - ``Someunknown-User.txt`` remains unchanged because the email is not found

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
