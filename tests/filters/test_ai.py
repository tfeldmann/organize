import json
import os
import pathlib
import uuid

import pytest
from conftest import make_files, read_files

from organize import Config
from organize.filters import ai, ai_providers
from organize.filters.ai import AI

CONFIG = """
rules:
  - locations: "/test"
    filters:
      - ai:
          categories: [invoice, receipt]
          extract: [vendor]
          min_confidence: 0.7
    actions:
      - move: "/docs/{ai.category}/{ai.vendor}/"
"""


class FakeAI:
    def __init__(self, *answers, error=None):
        self.answers = list(answers)
        self.error = error
        self.requests = []

    def __call__(self, **kwargs):
        self.requests.append(kwargs)
        if self.error:
            raise ai_providers.AnswerError(self.error)
        return json.dumps(self.answers.pop(0))

    def blocks(self, nr=0):
        return self.requests[nr]["parts"]


def answer(category, confidence=0.95, **fields):
    return dict(category=category, confidence=confidence, reason="", fields=fields)


@pytest.fixture(autouse=True)
def cache_dir(request, monkeypatch):
    # a fresh cache for each test, so answers never leak between tests
    if "fs" in request.fixturenames:
        request.getfixturevalue("fs")
        # created after pyfakefs is active, so it is a path in the fake filesystem
        path = pathlib.Path(f"/ai-cache-{uuid.uuid4().hex}")
    else:
        path = request.getfixturevalue("tmp_path") / "ai-cache"
    monkeypatch.setattr(ai, "CACHE_DIR", path)
    return path


@pytest.fixture
def claude(monkeypatch):
    def install(*answers, **kwargs):
        fake = FakeAI(*answers, **kwargs)
        monkeypatch.setattr(ai_providers, "ask", fake)
        return fake

    return install


def test_moves_by_category_and_field(fs, claude):
    fake = claude(answer("invoice", vendor="MegaCorp"))
    make_files({"scan.txt": "Invoice 12345\nMegaCorp Ltd."}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert read_files("docs") == {
        "invoice": {"MegaCorp": {"scan.txt": "Invoice 12345\nMegaCorp Ltd."}}
    }
    text = fake.blocks()[-1]["text"]
    assert "Invoice 12345" in text
    assert "File name: scan.txt" in text
    schema = fake.requests[0]["schema"]
    assert schema["properties"]["category"]["enum"] == ["invoice", "receipt", "other"]
    assert schema["properties"]["fields"]["required"] == ["vendor"]


def test_low_confidence_goes_to_review(fs, claude):
    claude(answer("receipt", confidence=0.4, vendor="Shop"))
    make_files({"doc.txt": "something"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert read_files("docs") == {"_Review": {"Shop": {"doc.txt": "something"}}}


def test_other_is_skipped(fs, claude):
    claude(answer("other", vendor=""))
    make_files({"notes.txt": "shopping list"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert read_files("test") == {"notes.txt": "shopping list"}


def test_fields_are_safe_for_paths(fs, claude):
    claude(answer("invoice", vendor="  ACME/Sub: GmbH. "))
    make_files({"a.txt": "x"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert read_files("docs") == {"invoice": {"ACME-Sub-GmbH": {"a.txt": "x"}}}


def test_missing_field_is_unknown(fs, claude):
    claude(answer("invoice", vendor=""))
    make_files({"a.txt": "x"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert read_files("docs") == {"invoice": {"Unknown": {"a.txt": "x"}}}


def test_results_are_cached(fs, claude):
    fake = claude(answer("invoice", vendor="A"))
    make_files({"a.txt": "same content"}, "test")
    Config.from_string(CONFIG).execute(simulate=True)
    Config.from_string(CONFIG).execute(simulate=False)
    assert len(fake.requests) == 1
    assert read_files("docs") == {"invoice": {"A": {"a.txt": "same content"}}}


def test_image_is_sent_to_claude(fs, claude):
    fake = claude(answer("receipt", vendor="Cafe"))
    make_files({"photo.jpg": b"\xff\xd8\xff fake jpeg"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    image = fake.blocks()[0]
    assert image["kind"] == "image"
    assert image["mime_type"] == "image/jpeg"


# a valid PDF with one empty page, like a scan without a text layer
BLANK_PDF = (
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


class Rejected(Exception):
    status_code = 400


def test_broken_pdf_is_not_sent(fs, claude):
    fake = claude(answer("other"))
    make_files({"broken.pdf": b"<html>not a pdf</html>"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert [p["kind"] for p in fake.blocks()] == ["text"]
    assert "not available" in fake.blocks()[0]["text"]


def test_rejected_file_is_classified_by_name(fs, monkeypatch):
    requests = []

    def ask(**kwargs):
        requests.append(kwargs["parts"])
        if len(requests) == 1:
            raise Rejected("The PDF specified was not valid.")
        return json.dumps(answer("invoice", vendor="X"))

    monkeypatch.setattr(ai_providers, "ask", ask)
    make_files({"invoice.pdf": BLANK_PDF}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert [p["kind"] for p in requests[0]] == ["pdf", "text"]
    assert [p["kind"] for p in requests[1]] == ["text"]
    assert read_files("docs") == {"invoice": {"X": {"invoice.pdf": BLANK_PDF.decode()}}}


def test_scanned_pdf_is_sent_as_document(fs, claude):
    fake = claude(answer("invoice", vendor="X"))
    make_files({"scan.pdf": BLANK_PDF}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert fake.blocks()[0]["kind"] == "pdf"
    assert fake.blocks()[0]["mime_type"] == "application/pdf"


def test_unknown_type_uses_metadata(fs, claude):
    fake = claude(answer("other"))
    make_files({"archive.zip": b"PK\x03\x04"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert len(fake.blocks()) == 1
    assert "not available" in fake.blocks()[0]["text"]


def test_refusal_leaves_file(fs, claude):
    claude(error="declined")
    make_files({"a.txt": "x"}, "test")
    Config.from_string(CONFIG).execute(simulate=False)
    assert read_files("test") == {"a.txt": "x"}


def test_long_text_is_shortened(fs, claude):
    fake = claude(answer("invoice", vendor="A"))
    make_files({"long.txt": "word " * 100}, "test")
    flt = AI(categories=["invoice"], max_chars=20, cache=False)
    flt.classify(ai.Path("/test/long.txt"))
    assert "Only the first 20 of" in fake.blocks()[-1]["text"]


@pytest.mark.parametrize("extract", [["category"], ["not valid"]])
def test_invalid_field_names(extract):
    with pytest.raises(ValueError):
        AI(categories=["invoice"], extract=extract)


def test_requires_categories():
    with pytest.raises(ValueError):
        AI()


def test_other_sorted_by_filetype(fs, claude):
    claude(answer("invoice", vendor="ACME"), answer("other", vendor=""))
    make_files({"bill.txt": "invoice", "poem.txt": "roses"}, "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            filters:
              - filetype
              - ai:
                  categories: [invoice]
                  extract: [vendor]
                  skip: []
            actions:
              - move: "/docs/{% if ai.category == 'other' %}{filetype}{% else %}{ai.category}/{ai.vendor}{% endif %}/"
        """
    ).execute(simulate=False)
    assert read_files("docs") == {
        "invoice": {"ACME": {"bill.txt": "invoice"}},
        "Documents": {"poem.txt": "roses"},
    }


def test_env_file_is_loaded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=from-env-file\n")
    ai_providers.load_env()
    assert os.environ["ANTHROPIC_API_KEY"] == "from-env-file"
    monkeypatch.delenv("ANTHROPIC_API_KEY")


def test_env_file_does_not_override(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-shell")
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=from-env-file\n")
    ai_providers.load_env()
    assert os.environ["ANTHROPIC_API_KEY"] == "from-shell"


def test_provider_and_default_model(fs, claude):
    fake = claude(answer("invoice"))
    make_files({"a.txt": "x"}, "test")
    AI(categories=["invoice"], provider="gemini", cache=False).classify(
        ai.Path("/test/a.txt")
    )
    assert fake.requests[0]["provider"] == "gemini"
    assert fake.requests[0]["model"] == "gemini-3.8-flash"


def test_audio_metadata_is_sent(fs, claude, monkeypatch):
    fake = claude(answer("other"))
    monkeypatch.setattr(
        ai, "media_metadata", lambda path: {"title": "Weekly sync", "duration": "1800"}
    )
    make_files({"rec.m4a": b"audio"}, "test")
    AI(categories=["meeting"], cache=False).classify(ai.Path("/test/rec.m4a"))
    text = fake.blocks()[-1]["text"]
    assert "Title: Weekly sync" in text
    assert "Duration: 1800 seconds" in text
    assert "(Audio)" in text


FOLDER_CONFIG = """
rules:
  - locations: "/test"
    subfolders: false
    targets: dirs
    filters:
      - ai:
          categories: [invoice, tax]
          skip: []
    actions:
      - move: "/test/{% if ai.category == 'other' %}{ai.filetype}{% else %}{ai.category}{% endif %}/"
"""


def test_folder_is_moved_as_a_whole(fs, claude):
    fake = claude(answer("tax"))
    make_files({"Steuer 2025": {"a.pdf": "A", "sub": {"b.txt": "B"}}}, "test")
    Config.from_string(FOLDER_CONFIG).execute(simulate=False)
    assert read_files("test") == {
        "tax": {"Steuer 2025": {"a.pdf": "A", "sub": {"b.txt": "B"}}}
    }
    text = fake.blocks()[0]["text"]
    assert "Folder name: Steuer 2025" in text
    assert "Contains 1 files and 1 folders: 1 Documents" in text
    assert "- a.pdf" in text and "- sub/" in text
    assert len(fake.blocks()) == 1  # only names, no file content


def test_target_folders_are_not_moved(fs, claude):
    fake = claude(answer("other"))
    make_files(
        {
            "Invoice": {"x.pdf": ""},
            "_Review": {},
            "Archives": {"a.zip": ""},
            "Folders": {},
            "Random stuff": {},
        },
        "test",
    )
    Config.from_string(FOLDER_CONFIG).execute(simulate=False)
    assert len(fake.requests) == 1
    assert read_files("test") == {
        "Invoice": {"x.pdf": ""},
        "_Review": {},
        "Archives": {"a.zip": ""},
        "Folders": {"Random stuff": {}},
    }


def test_app_bundle_goes_to_installers(fs, claude):
    claude(answer("other"))
    make_files({"Tool.app": {"Contents": {"Info.plist": ""}}}, "test")
    Config.from_string(FOLDER_CONFIG).execute(simulate=False)
    assert read_files("test") == {
        "Installers": {"Tool.app": {"Contents": {"Info.plist": ""}}}
    }


def test_folder_cache_depends_on_content(fs):
    make_files({"f": {"a.txt": ""}}, "test")
    flt = AI(categories=["invoice"])
    key = flt._cache_key(ai.Path("/test/f"))
    make_files({"b.txt": ""}, "test/f")
    assert flt._cache_key(ai.Path("/test/f")) != key


def test_long_folder_listing_is_shortened(fs, claude):
    make_files({f"file{i:03}.txt": "" for i in range(50)}, "test/many")
    text = AI(categories=["invoice"])._folder_parts(ai.Path("/test/many"))[0]["text"]
    assert "- file039.txt" in text
    assert "- file040.txt" not in text
    assert "... and 10 more" in text
