"""
Classify files with AI by file type and content.

The filter extracts the text of a file (or sends images and scanned PDFs as-is,
or the tags of audio and video files), asks an AI model to pick one of the
configured categories and to extract a set of fields, and stores the result in
`{ai.*}` so actions can build target paths from it.
"""

import base64
import hashlib
import io
import json
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

import platformdirs
from pydantic import Field, field_validator
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.logger import logger
from organize.output import Output
from organize.resource import Resource
from organize.utils import safe_path_part
from organize.validators import FlatList

from . import ai_providers
from .ai_providers import DEFAULT_MODELS, Effort, Part, Provider
from .filecontent import EXTRACTORS, pdf_bytes, textract
from .filetype import ALL_GROUPS, FOLDER_GROUP, file_group
from .media import describe, media_metadata
from .mimetype import guess_mimetype

# Bump whenever the prompt or schema changes so cached results are not reused.
PROMPT_VERSION = 3

CACHE_DIR = platformdirs.user_cache_path(appname="organize") / "ai"

IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_PDF_BYTES = 30 * 1024 * 1024

# PDFs with less extracted text than this are treated as scans.
MIN_PDF_TEXT = 50

# How many entries of a folder are listed for the model.
MAX_FOLDER_ENTRIES = 40

FALLBACK_CATEGORY = "other"

SYSTEM_PROMPT = """\
You sort a user's files into folders. For each file you get its name, type and size, \
and usually its content or metadata. Pick the single category that best describes \
what the file is, judging mainly by its content and using the name and type as \
supporting evidence. Use "other" when no category fits.

Folders are sorted as a whole. For a folder you get its name and a list of what it \
contains; judge mainly by the name.

Report your confidence between 0 and 1: 0.9 or higher only when the content clearly \
shows the category, below 0.5 when you are guessing.

For each requested field, return the value as it appears in the file, short enough \
to be used as a folder or file name. Return an empty string when the file does not \
contain the value - never invent one."""


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class AI:
    """Classifies files with AI based on their type and content.

    Text is extracted from .pdf, .docx, .txt, .md and .log files. Images
    (.jpg, .png, .gif, .webp) and scanned PDFs without a text layer are sent to the
    model directly. For audio and video files their metadata (title, artist, album,
    duration, ...) is sent. All other files are classified by name, type and size.

    Folders (with `targets: dirs`) are classified by their name and the names of the
    files they contain, and moved as a whole. Folders named like a category, the
    `uncertain` category or a [file type](#filetype) (e.g. `invoice` or `Archives`)
    are never matched, so the folders created by your rules stay where they are.

    An "other" category is always available in addition to the configured ones.
    Files in this category are left alone unless you change `skip`.
    Results are cached by file content, so a file is only sent once per
    configuration.

    Supported providers are `anthropic` (Claude), `openai` and `gemini`. They need an
    API key in `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or `GEMINI_API_KEY`, which can
    also be set in a `.env` file in the current directory or next to your config
    files (`organize show --path` shows where they are).
    The file content is sent to the chosen provider.

    Attributes:
        categories (list(str) or dict(str, str)):
            The categories to choose from. Either a list of names or a mapping of
            name to a description that helps the model decide.
        extract (list(str) or dict(str, str)):
            Fields to extract from the file (e.g. `vendor`, `date`). Either a list of
            names or a mapping of name to a description of the expected value.
        skip (list(str)):
            Files put in one of these categories do not match, so the rule leaves
            them alone. Defaults to `other`.
        min_confidence (float):
            Results below this confidence get the `uncertain` category.
            Defaults to 0.
        uncertain (str):
            The category assigned to results below `min_confidence`.
            Defaults to `_Review`.
        instructions (str):
            Additional instructions for the model, e.g. about your documents.
        provider (str):
            `anthropic`, `openai` or `gemini`. Defaults to `anthropic`.
        model (str):
            The model to use. Defaults to `claude-opus-5-5` (anthropic),
            `gpt-6.1-sol` (openai) or `gemini-3.8-flash` (gemini).
        effort (str):
            How much the model thinks before answering
            (`low`, `medium`, `high`, `xhigh`, `max`). Defaults to `low`.
        max_chars (int):
            Maximum number of characters of extracted text sent to the model. Longer
            texts are shortened and the model is told so. Defaults to 50000.
        cache (bool):
            Whether to cache results by file content. Defaults to `true`.

    **Returns:**

    - `{ai.category}`: The chosen category
    - `{ai.confidence}`: The model's confidence from 0 to 1
    - `{ai.reason}`: A short explanation of the choice
    - `{ai.filetype}`: The [type](#filetype) of the file, e.g. `Documents`, or
      `Folders` for folders
    - `{ai.<field>}`: The extracted value of each field in `extract`, made safe to use
      in paths (`Unknown` if the file does not contain it)

    You can test the filter on any file by running:

    ```sh
    python -m organize.filters.ai "/path/to/file.pdf" invoice receipt contract
    ```
    """

    categories: Dict[str, str] = Field(default_factory=dict)
    extract: Dict[str, str] = Field(default_factory=dict)
    skip: FlatList[str] = Field(default_factory=lambda: [FALLBACK_CATEGORY])
    min_confidence: float = 0.0
    uncertain: str = "_Review"
    instructions: str = ""
    provider: Provider = "anthropic"
    model: Optional[str] = None
    effort: Effort = "low"
    max_chars: int = 50_000
    cache: bool = True

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="ai",
        files=True,
        dirs=True,
    )

    @field_validator("categories", "extract", mode="before")
    @classmethod
    def ensure_mapping(cls, value):
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            value = {str(x): "" for x in value}
        return value

    @field_validator("extract", mode="after")
    @classmethod
    def check_field_names(cls, value):
        for name in value:
            if not name.isidentifier():
                raise ValueError(f'Field name "{name}" must be a valid identifier')
            if name in ("category", "confidence", "reason", "filetype"):
                raise ValueError(f'Field name "{name}" is reserved')
        return value

    def __post_init__(self):
        if not self.categories:
            raise ValueError("Please specify at least one category")
        self._categories = dict(self.categories)
        self._categories.setdefault(FALLBACK_CATEGORY, "Nothing else fits.")
        self._fields = dict(self.extract)
        self._model = self.model or DEFAULT_MODELS[self.provider]
        # folders with these names are targets of the rules and must stay
        self._reserved = {
            x.lower() for x in (*self._categories, self.uncertain, *ALL_GROUPS)
        }

    def _schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": list(self._categories)},
                "confidence": {"type": "number"},
                "reason": {"type": "string"},
                "fields": {
                    "type": "object",
                    "properties": {name: {"type": "string"} for name in self._fields},
                    "required": list(self._fields),
                    "additionalProperties": False,
                },
            },
            "required": ["category", "confidence", "reason", "fields"],
            "additionalProperties": False,
        }

    def _task(self) -> str:
        lines = ["Categories:"]
        for name, desc in self._categories.items():
            lines.append(f"- {name}: {desc}" if desc else f"- {name}")
        if self._fields:
            lines.append("\nFields to extract:")
            for name, desc in self._fields.items():
                lines.append(f"- {name}: {desc}" if desc else f"- {name}")
        if self.instructions:
            lines.append(f"\nAdditional instructions:\n{self.instructions}")
        return "\n".join(lines)

    def _folder_parts(self, path: Path) -> List[Part]:
        entries = sorted(
            (e for e in path.iterdir() if not e.name.startswith(".")),
            key=lambda e: e.name.lower(),
        )
        dirs = [e for e in entries if e.is_dir()]
        files = [e for e in entries if not e.is_dir()]
        groups: Dict[str, int] = {}
        for e in files:
            groups[file_group(e.name)] = groups.get(file_group(e.name), 0) + 1
        info = (
            f"Folder name: {path.name}\n"
            f"Contains {len(files)} files and {len(dirs)} folders"
        )
        if groups:
            info += ": " + ", ".join(f"{n} {g}" for g, n in sorted(groups.items()))
        if entries:
            info += "\n\nEntries:\n" + "\n".join(
                f"- {e.name}/" if e.is_dir() else f"- {e.name}"
                for e in entries[:MAX_FOLDER_ENTRIES]
            )
            if len(entries) > MAX_FOLDER_ENTRIES:
                info += f"\n- ... and {len(entries) - MAX_FOLDER_ENTRIES} more"
        return [{"kind": "text", "text": f"{info}\n\n{self._task()}"}]

    def _parts(self, path: Path, send_files: bool = True) -> List[Part]:
        if path.is_dir():
            return self._folder_parts(path)
        suffix = path.suffix.lower()
        size = path.stat().st_size
        group = file_group(path.name)
        info = (
            f"File name: {path.name}\n"
            f"Type: {guess_mimetype(path) or 'unknown'} ({group})\n"
            f"Size: {size} bytes"
        )
        parts: List[Part] = []

        text = ""
        if suffix in EXTRACTORS:
            try:
                text = textract(path).strip()
            except Exception as e:
                logger.warning("Could not extract text from %s: %s", path, e)

        if suffix == ".pdf" and len(text) < MIN_PDF_TEXT:
            # most likely a scan - let the model read the pages
            if not send_files:
                pass
            elif size > MAX_PDF_BYTES:
                logger.warning("%s is too large to send as PDF", path)
            else:
                data = pdf_bytes(path)
                if data is None or not _is_readable_pdf(data):
                    logger.warning("%s is not a readable PDF", path)
                else:
                    parts.append(_binary_part("pdf", "application/pdf", path, data))
                    text = ""
        elif suffix in IMAGE_TYPES and send_files:
            if size <= MAX_IMAGE_BYTES:
                parts.append(_binary_part("image", IMAGE_TYPES[suffix], path))
            else:
                logger.warning("%s is too large to send as image", path)
        elif group in ("Audio", "Videos"):
            text = describe(media_metadata(path)) or ""

        if text:
            if len(text) > self.max_chars:
                info += (
                    f"\nOnly the first {self.max_chars} of {len(text)} characters "
                    "of the content are shown."
                )
                text = text[: self.max_chars]
            info += f"\n\nContent:\n<content>\n{text}\n</content>"
        elif not parts:
            info += "\n\nThe content is not available; decide by name and type."

        parts.append({"kind": "text", "text": f"{info}\n\n{self._task()}"})
        return parts

    def _cache_key(self, path: Path) -> str:
        digest = hashlib.sha256()
        if path.is_dir():
            # a folder is identified by its name and what is in it
            digest.update(self._folder_parts(path)[0]["text"].encode("utf-8"))
        else:
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    digest.update(chunk)
        settings = json.dumps(
            [
                PROMPT_VERSION,
                self.provider,
                self._model,
                self._categories,
                self._fields,
                self.instructions,
                self.max_chars,
                path.suffix.lower(),
            ],
            sort_keys=True,
        )
        digest.update(settings.encode("utf-8"))
        return digest.hexdigest()

    def classify(self, path: Path) -> Dict[str, Any]:
        """Returns the model's raw answer, using the cache if possible."""
        cache_file = CACHE_DIR / f"{self._cache_key(path)}.json"
        if self.cache and cache_file.exists():
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))
            except ValueError:
                pass  # broken cache entry, ask again

        def ask(parts: List[Part]) -> str:
            return ai_providers.ask(
                provider=self.provider,
                model=self._model,
                effort=self.effort,
                system=SYSTEM_PROMPT,
                schema=self._schema(),
                parts=parts,
            )

        parts = self._parts(path)
        try:
            try:
                answer = ask(parts)
            except Exception as e:
                # the provider may reject a broken or protected PDF or image - then
                # classify the file by its name and type instead
                if not ai_providers.is_invalid_input(e) or len(parts) == 1:
                    raise
                logger.warning(
                    "%s was rejected (%s), retrying without content", path, e
                )
                answer = ask(self._parts(path, send_files=False))
        except ai_providers.AnswerError as e:
            raise ValueError(f"Could not classify {path.name}: {e}") from e
        result = json.loads(answer)

        if self.cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(result), encoding="utf-8")
        return result

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        is_dir = res.path.is_dir()
        if is_dir and res.path.name.lower() in self._reserved:
            return False
        result = self.classify(res.path)

        category = result["category"]
        confidence = min(max(float(result["confidence"]), 0.0), 1.0)
        if category not in self._categories:
            category = FALLBACK_CATEGORY
        if category in self.skip:
            return False
        if confidence < self.min_confidence:
            category = self.uncertain

        fields = result.get("fields", {})
        res.vars[self.filter_config.name] = {
            "category": category,
            "confidence": confidence,
            "reason": result.get("reason", ""),
            "filetype": _filetype(res.path.name, is_dir),
            **{name: safe_path_part(fields.get(name, "")) for name in self._fields},
        }
        return True


def _filetype(name: str, is_dir: bool) -> str:
    group = file_group(name)
    if is_dir and group not in ("Installers", "Ebooks"):
        # folders are only grouped by their extension if they are bundles
        return FOLDER_GROUP
    return group


def _is_readable_pdf(data: bytes) -> bool:
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    try:
        # fails for broken or password protected files
        doc = PDFDocument(PDFParser(io.BytesIO(data)))
        return next(PDFPage.create_pages(doc), None) is not None
    except Exception:
        return False


def _binary_part(
    kind: str, mime_type: str, path: Path, data: Optional[bytes] = None
) -> Part:
    if data is None:
        data = path.read_bytes()
    return {
        "kind": kind,
        "mime_type": mime_type,
        "filename": path.name,
        "data": base64.standard_b64encode(data).decode("utf-8"),
    }


if __name__ == "__main__":
    import sys

    categories = sys.argv[2:] or ["invoice", "receipt", "contract"]
    flt = AI(categories={name: "" for name in categories}, cache=False)
    print(json.dumps(flt.classify(Path(sys.argv[1])), indent=2))
