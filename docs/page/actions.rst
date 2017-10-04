Actions
=======

Move
----
.. py:class:: Move(dest, [overwrite=False])

    Move files

    :param str dest:
        can be a format string which uses file attributes from a filter.
        If `dest` is a folder path, the file will be moved into this folder and
        not renamed.

    :param bool overwrite:
        specifies whether existing files should be overwritten.
        Otherwise it will start enumerating files (append a counter to the
        filename) to resolve naming conflicts.

    Example usage in :ref:`configuration`:

    .. code-block:: yaml

        Move: {dest: '/some/folder/'}
        Move: {dest: '/some/path/some-name-{year}-{month:02}-{day:02}.pdf'}
        Move: {dest: '{path.parent}/Invoice', overwrite: False}

Shell
-----

Echo
----
.. py:class:: Echo(msg)

    Prints the given (formatted) message

    :param str msg: The message to print (can be formatted)

    Example usage in :ref:`configuration`:

    .. code-block:: yaml

        ...
        rules:
        - folders: *all
        filters:
        - Regex: {expr: '.*'}
        actions:
        - Echo: {msg: 'Hello, World! "{path.name}/new/asd"'}
