import logging
import textwrap
from typing import Any, Mapping, Optional, Iterable

from organize.utils import DotDict

from .action import Action

logger = logging.getLogger(__name__)


class Python(Action):

    r"""
    Execute python code in your config file.

    :param str code: The python code to execute

    Examples:
      - A basic example that shows how to get the current file path and do some
        printing in a for loop. The ``|`` is yaml syntax for defining a string
        literal spanning multiple lines.

        .. code-block:: yaml
            :caption: config.yaml

            rules:
            - folders: '~/Desktop'
              actions:
                - python: |
                    print('The path of the current file is %s' % path)
                    for _ in range(5):
                        print('Heyho, its me from the loop')

      - You can access filter data:

        .. code-block:: yaml
            :caption: config.yaml

            rules:
            - folders: ~/Desktop
              filters:
                - regex: '^(?P<name>.*)\.(?P<extension>.*)$'
              actions:
                - python: |
                    print('Name: %s' % regex.name)
                    print('Extension: %s' % regex.extension)

      - You have access to all the python magic -- do a google search for each
        filename starting with an underscore:

        .. code-block:: yaml
            :caption: config.yaml

            rules:
            - folders: ~/Desktop
              filters:
                - filename:
                    startswith: '_'
              actions:
                - python: |
                    import webbrowser
                    webbrowser.open('https://www.google.com/search?q=%s' % path.stem)
    """

    def __init__(self, code) -> None:
        self.code = textwrap.dedent(code)

    def usercode(self, *args, **kwargs) -> Optional[Any]:
        pass  # will be overwritten by `create_method`

    def create_method(self, name: str, argnames: Iterable[str], code: str) -> None:
        globals_ = globals().copy()
        globals_["print"] = self.print
        locals_ = locals().copy()
        funccode = "def {fnc}__({arg}):\n{cod}\n\nself.{fnc} = {fnc}__\n".format(
            fnc=name,
            arg=", ".join(argnames),
            cod=textwrap.indent(textwrap.dedent(code), " " * 4),
        )
        exec(funccode, globals_, locals_)  # pylint: disable=exec-used

    def pipeline(self, args: DotDict) -> Optional[Mapping[str, Any]]:
        simulate = args.simulate
        if simulate:
            self.print("Code not run in simulation. (Args: %s)" % args)
            return None

        logger.info('Executing python:\n"""\n%s\n""", args=%s', self.code, args)
        self.create_method(name="usercode", argnames=args.keys(), code=self.code)
        self.print("Running python script.")

        result = self.usercode(**args)  # pylint: disable=assignment-from-no-return
        return result
