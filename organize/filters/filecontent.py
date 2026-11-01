import base64
import binascii
import io
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Callable, ClassVar, Dict, Optional, Union

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.logger import logger
from organize.output import Output
from organize.resource import Resource
from organize.utils import has_executable


def _compress_chars(inp: str) -> str:
    # Compress lines consisting only of separated chars ("H e l l o  W o r l d")
    result = []
    for line in inp.splitlines():
        if re.match(r"^(\S +)+\S$", line):
            result.append(re.sub(r"(\S) ", repl=r"\g<1>", string=line))
        else:
            result.append(line)
    return "\n".join(result)


def _remove_nls(inp: str) -> str:
    # remove superfluous newlines
    return re.sub(pattern=r"\n{3,}", repl="\n\n", string=inp, flags=re.MULTILINE)


def clean(inp: str) -> str:
    return _remove_nls(_compress_chars(inp))


def extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _pdftotext_available() -> bool:
    # check whether the given path is executable
    ok = has_executable(name="pdftotext")
    if not ok:
        logger.warning("pdftotext not available. Falling back to pdfminer library.")
    return ok


def _extract_with_pdftotext(path: Path, keep_layout: bool) -> str:
    if keep_layout:
        args = ["-layout", str(path), "-"]
    else:
        args = [str(path), "-"]
    result = subprocess.check_output(
        ("pdftotext", *args),
        text=True,
        stderr=subprocess.DEVNULL,
    )
    return clean(result)


def _extract_with_pdfminer(path: Path) -> str:
    from pdfminer import high_level

    return clean(high_level.extract_text(path))


def unwrap_mime_pdf(data: bytes) -> Optional[bytes]:
    """
    Some websites deliver PDFs wrapped in a MIME message part
    (starting with `------=_Part...`). Returns the contained PDF, if any.
    """
    if not data.startswith(b"--"):
        return None
    boundary = data.split(b"\n", 1)[0].strip()
    parts = data.split(boundary)
    for part in parts[1:]:
        head, sep, body = part.partition(b"\r\n\r\n")
        if not sep:
            head, sep, body = part.partition(b"\n\n")
        if b"application/pdf" not in head.lower():
            continue
        # the line break before the next boundary belongs to the boundary
        if body.endswith(b"\r\n"):
            body = body[:-2]
        elif body.endswith(b"\n"):
            body = body[:-1]
        if b"base64" in head.lower():
            try:
                body = base64.b64decode(body)
            except binascii.Error:
                continue
        if body.startswith(b"%PDF-"):
            return body
    return None


def pdf_bytes(path: Path) -> Optional[bytes]:
    """The PDF data of a file, unwrapping MIME wrapped PDFs. None if no PDF."""
    data = path.read_bytes()
    if data.startswith(b"%PDF-"):
        return data
    return unwrap_mime_pdf(data)


def extract_pdf(path: Path, keep_layout: bool = True) -> str:
    with path.open("rb") as f:
        is_plain_pdf = f.read(5) == b"%PDF-"
    if not is_plain_pdf:
        data = pdf_bytes(path)
        if data is not None:
            from pdfminer import high_level

            return clean(high_level.extract_text(io.BytesIO(data)))
    if _pdftotext_available():
        return _extract_with_pdftotext(path=path, keep_layout=keep_layout)
    return _extract_with_pdfminer(path=path)


def extract_docx(path: Path) -> str:
    import docx2txt  # type: ignore

    result = docx2txt.process(path)
    return clean(result)


EXTRACTORS: Dict[str, Callable[[Path], str]] = {
    ".md": extract_txt,
    ".txt": extract_txt,
    ".log": extract_txt,
    ".pdf": extract_pdf,
    ".docx": extract_docx,
}


def textract(path: Path) -> str:
    extractor = EXTRACTORS[path.suffix.lower()]
    return extractor(path)


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class FileContent:
    """Matches file content with the given regular expression.

    Supports .md, .txt, .log, .pdf and .docx files.

    For PDF content extraction poppler should be installed for the `pdftotext` command.
    If this is not available `filecontent` will fall back to the `pdfminer` library.

    Attributes:
        expr (str): The regular expression to be matched.

    Any named groups (`(?P<groupname>.*)`) in your regular expression will
    be returned like this:

    **Returns:**

    - `{filecontent.groupname}`: The text matched with the named group
      `(?P<groupname>)`

    You can test the filter on any file by running:

    ```sh
    python -m organize.filters.filecontent "/path/to/file.pdf"
    ```
    """

    expr: str = r"(?P<all>.*)"

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="filecontent",
        files=True,
        dirs=False,
    )

    def __post_init__(self):
        self._expr = re.compile(self.expr, re.MULTILINE | re.DOTALL)

    def matches(self, path: Path) -> Union[re.Match, None]:
        try:
            content = textract(path)
            match = self._expr.search(content)
            return match
        except Exception:
            return None

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        match = self.matches(path=res.path)

        if match:
            res.deep_merge(self.filter_config.name, match.groupdict())
        return bool(match)


if __name__ == "__main__":
    import sys

    print(textract(Path(sys.argv[1])))
