import logging
from organize.utils import Path
from .action import Action

logger = logging.getLogger(__name__)


class Python(Action):

    """
    Execute python code in your config file.

    :param str code: The python code to execute

    Example:
      - A basic example that shows how to get the current file path and do some
        printing in a for loop. The ``|`` is yaml syntax for defining a string
        literal spanning multiple lines.

        .. code-block:: yaml

          rules:
            - folders: '~/Desktop'
              actions:
              - Python: |
                  print('The path of the current file is %s' % path)
                  print('This is how you inline python code!')
                  print('You have access to the folloging variables:')
                  print(path)
                  print(simulate)
                  for _ in range(5):
                      print('Heyho, its me from the loop')
    """

    def __init__(self, code):
        self.code = code

    def run(self, path, attrs, simulate):  # type: (Path, dict, bool) -> None
        if simulate:
            self.print('Code not run in simulation')
        else:
            # local variables for inline function
            locals_ = attrs.copy()
            locals_['simulate'] = simulate
            locals_['path'] = path
            # replace default print function
            globals_ = globals().copy()
            globals_['print'] = self.print
            exec(self.code, globals_, locals_)
