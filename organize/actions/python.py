import logging
import textwrap

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

    def __init__(self, code):
        self.code = textwrap.dedent(code)

        # the user's code becomes a method of the filter instance
        self.method = (
            "def _usercode(args):\n"
            + textwrap.indent(self.code, "    ")
            + "\n"
            + "self.usercode = _usercode"
        )
        globals_ = globals().copy()
        globals_["print"] = self.print
        exec(self.method, globals_, {"self": self})

    def usercode(self, args):
        raise NotImplementedError("No user code given")

    def pipeline(self, args):
        simulate = args.simulate
        if simulate:
            self.print("Code not run in simulation (args=%s)" % args)
        else:
            logger.info(
                'Executing python script:\n"""\n%s""", args=%s',
                self.code,
                args,
            )
            return self.usercode(args)
