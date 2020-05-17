import sys

# in python < 3.6 the pathlib module misses some features so we have to import
# a backported alternative
if sys.version_info < (3, 6):
    from pathlib2 import Path  # type: ignore
else:
    from pathlib import Path
