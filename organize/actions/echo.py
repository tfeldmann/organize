import logging

from .action import Action

logger = logging.getLogger(__name__)

from ..utils import JinjaEnv


class Echo(Action):

    """
    Prints the given (formatted) message. This can be useful to test your rules,
    especially if you use formatted messages.

    :param str msg: The message to print (can be formatted)

    Example:
        - Prints "Found old file" for each file older than one year:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - lastmodified:
                      days: 365
                actions:
                  - echo: 'Found old file'

        - Prints "Hello World!" and filepath for each file on the desktop:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders:
                  - ~/Desktop
                actions:
                  - echo: 'Hello World! {path}'

        - This will print something like ``Found a PNG: "test.png"`` for each
          file on your desktop:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders:
                  - ~/Desktop
                filters:
                  - Extension
                actions:
                  - echo: 'Found a {extension.upper}: "{path.name}"'

        - Show the ``{basedir}`` and ``{path}`` of all files in '~/Downloads',
          '~/Desktop' and their subfolders:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders:
                  - ~/Desktop
                  - ~/Downloads
                subfolders: true
                actions:
                  - echo: 'Basedir: {basedir}'
                  - echo: 'Path:    {path}'
    """

    name = "echo"

    @classmethod
    def get_schema(cls):
        return {cls.name: str}

    def __init__(self, msg) -> None:
        self.msg = JinjaEnv.from_string(msg)
        self.log = logging.getLogger(__name__)

    def pipeline(self, args: dict, simulate: bool) -> None:
        full_msg = self.msg.render(**args)
        self.print("%s" % full_msg)

    def __str__(self) -> str:
        return 'Echo(msg="%s")' % self.msg
