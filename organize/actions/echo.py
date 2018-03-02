import logging
from .action import Action


class Echo(Action):

    """
    Prints the given (formatted) message. This can be useful to test your rules,
    especially if you use formatted messages.

    :param str msg: The message to print (can be formatted)

    Example:
        - Prints "Hello World!" and filepath for each file on the desktop:

          .. code-block:: yaml

            # config.yaml
            rules:
              - folders:
                  - ~/Desktop
                actions:
                  - Echo: "Hello World! {path}"

        - This will print something like ``Found a PNG: "test.png"`` for each
          file on your desktop:

          .. code-block:: yaml

            # config.yaml
            rules:
              - folders:
                  - ~/Desktop
                filters:
                  - Extension
                actions:
                  - Echo: 'Found a {extension.upper}: "{path.name}"'
    """

    def __init__(self, msg):
        self.msg = msg
        self.log = logging.getLogger(__name__)

    def run(self, path, attrs, simulate):
        self.log.debug(
            'Echo msg "%s" for path: "%s" with attrs: "%s"',
            self.msg, path, attrs)
        full_msg = self.fill_template_tags(self.msg, path, attrs)
        self.log.info('Console output: %s', full_msg)
        self.print('%s' % full_msg)

    def __str__(self):
        return 'Echo(msg="%s")' % self.msg
