.. _actions:

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
        filename) to resolve naming conflicts. [Default: False]

    Example usage in :ref:`configuration`:

    .. code-block:: yaml

        # Move into /some/folder/ and keep filenames
        - Move: {dest: '/some/folder/'}

        # Move to /some/path/ and change the name to include the full date
        - Move: {dest: '/some/path/some-name-{year}-{month:02}-{day:02}.pdf'}

        # Move into the folder `Invoices` on the same folder level as the file
        # itself. Keep the filename but do not overwrite existing files (adds
        # an index to the file).
        - Move: {dest: '{path.parent}/Invoices', overwrite: False}

    If the specified folders do not exist they will be created when running.

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
