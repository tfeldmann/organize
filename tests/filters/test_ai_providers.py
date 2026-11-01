from types import SimpleNamespace

import pytest

from organize.filters import ai_providers
from organize.filters.ai_providers import AnswerError, ask

PARTS = [
    {"kind": "image", "mime_type": "image/png", "filename": "a.png", "data": "AAA"},
    {"kind": "pdf", "mime_type": "application/pdf", "filename": "b.pdf", "data": "BBB"},
    {"kind": "text", "text": "hello"},
]
SCHEMA = {"type": "object"}


class Recorder:
    """Records the keyword arguments of the SDK call and returns `response`."""

    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return self.response


def install(monkeypatch, provider, client):
    monkeypatch.setattr(ai_providers, "get_client", lambda p: client)


def _ask(provider, model, effort="low"):
    return ask(provider, model, effort, "system", SCHEMA, PARTS)


def anthropic_client(stop_reason="end_turn"):
    text = SimpleNamespace(type="text", text='{"ok": 1}')
    create = Recorder(SimpleNamespace(stop_reason=stop_reason, content=[text]))
    messages = SimpleNamespace(create=create)
    return SimpleNamespace(messages=messages, beta=SimpleNamespace(messages=messages))


def test_anthropic(monkeypatch):
    client = anthropic_client()
    install(monkeypatch, "anthropic", client)
    assert _ask("anthropic", "claude-opus-5-5") == '{"ok": 1}'
    kwargs = client.messages.create.kwargs
    assert kwargs["fallbacks"] == "default"
    assert kwargs["output_config"]["format"]["schema"] == SCHEMA
    image, doc, text = kwargs["messages"][0]["content"]
    assert image["type"] == "image" and image["source"]["data"] == "AAA"
    assert doc["type"] == "document"
    assert text == {"type": "text", "text": "hello"}


def test_anthropic_without_fallbacks(monkeypatch):
    client = anthropic_client()
    install(monkeypatch, "anthropic", client)
    _ask("anthropic", "claude-haiku-5-5")
    assert "fallbacks" not in client.messages.create.kwargs


def test_anthropic_refusal(monkeypatch):
    install(monkeypatch, "anthropic", anthropic_client(stop_reason="refusal"))
    with pytest.raises(AnswerError):
        _ask("anthropic", "claude-opus-5-5")


def openai_client(status="completed", output_text='{"ok": 1}'):
    create = Recorder(SimpleNamespace(status=status, output_text=output_text))
    return SimpleNamespace(responses=SimpleNamespace(create=create))


def test_openai(monkeypatch):
    client = openai_client()
    install(monkeypatch, "openai", client)
    assert _ask("openai", "gpt-6.1-sol", effort="high") == '{"ok": 1}'
    kwargs = client.responses.create.kwargs
    assert kwargs["instructions"] == "system"
    assert kwargs["reasoning"] == {"effort": "high"}
    assert kwargs["text"]["format"]["strict"] is True
    image, doc, text = kwargs["input"][0]["content"]
    assert image == {"type": "input_image", "image_url": "data:image/png;base64,AAA"}
    assert doc["file_data"] == "data:application/pdf;base64,BBB"
    assert doc["filename"] == "b.pdf"
    assert text == {"type": "input_text", "text": "hello"}


@pytest.mark.parametrize("status, text", [("incomplete", "{}"), ("completed", "")])
def test_openai_errors(monkeypatch, status, text):
    install(monkeypatch, "openai", openai_client(status=status, output_text=text))
    with pytest.raises(AnswerError):
        _ask("openai", "gpt-6.1-sol")


def gemini_client(status="completed"):
    create = Recorder(SimpleNamespace(status=status, output_text='{"ok": 1}'))
    return SimpleNamespace(interactions=SimpleNamespace(create=create))


def test_gemini(monkeypatch):
    client = gemini_client()
    install(monkeypatch, "gemini", client)
    assert _ask("gemini", "gemini-3.8-flash", effort="max") == '{"ok": 1}'
    kwargs = client.interactions.create.kwargs
    assert kwargs["system_instruction"] == "system"
    assert kwargs["generation_config"]["thinking_level"] == "high"
    assert kwargs["response_format"]["schema"] == SCHEMA
    image, doc, text = kwargs["input"]
    assert image == {"type": "image", "data": "AAA", "mime_type": "image/png"}
    assert doc["type"] == "document"
    assert text == {"type": "text", "text": "hello"}


def test_gemini_error(monkeypatch):
    install(monkeypatch, "gemini", gemini_client(status="failed"))
    with pytest.raises(AnswerError):
        _ask("gemini", "gemini-3.8-flash")
