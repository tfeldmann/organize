import logging
from organize.utils import Path
from .action import Action


class Python(Action):

    """
    Execute python code in your config file.

    :param str code: The python code to execute

    Examples:
      - A basic example that shows how to get the current file path and do some
        printing in a for loop. The ``|`` is yaml syntax for defining a string
        literal spanning multiple lines.

        .. code-block:: yaml

          # config.yaml
          rules:
            - folders: '~/Desktop'
              actions:
                - Python: |
                    print('The path of the current file is %s' % path)
                    for _ in range(5):
                        print('Heyho, its me from the loop')

      - You can access filter data:

        .. code-block:: yaml

          # config.yaml
          rules:
            - folders: ~/Desktop
              filters:
                - Regex: '^(?P<name>.*)\.(?P<extension>.*)$'
              actions:
                - Python: |
                    print('Name: %s' % regex.name)
                    print('Extension: %s' % regex.extension)

      - You have access to all the python magic -- do a google search for each
        filename starting with an underscore:

        .. code-block:: yaml

          # config.yaml
          rules:
            - folders: ~/Desktop
              filters:
                - Filename:
                    startswith: '_'
              actions:
                - Python: |
                    import webbrowser
                    webbrowser.open('https://www.google.com/search?q=%s' % path.stem)
    """

    def __init__(self, code):
        self.code = code
        self.log = logging.getLogger(__name__)

    def run(self, basedir: Path, path: Path, attrs: dict, simulate: bool):
        if simulate:
            self.print('Code not run in simulation')
        else:
            self.log.info(
                'Executing python script:\n"""\n%s""" with path="%s", args=%s',
                self.code, path, attrs)
            # local variables for inline function
            locals_ = attrs.copy()
            locals_['simulate'] = simulate
            locals_['path'] = path
            locals_['basedir'] = basedir
            # replace default print function
            globals_ = globals().copy()
            globals_['print'] = self.print
            exec(self.code, globals_, locals_)
