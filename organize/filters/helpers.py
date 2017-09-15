import pathlib
import logging

logger = logging.getLogger('Dry run')


def parse_pdf(path: pathlib.Path):
    import slate3k
    with path.open('rb') as f:
        return slate3k.PDF(f)
