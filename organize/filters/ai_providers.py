"""
Thin adapters that send one classification request to an AI provider and return
the JSON text of the answer.

A request consists of a system prompt, a JSON schema for the answer and a list of
parts. Each part is a dict with a `kind` of `text` (with `text`), `image` or `pdf`
(with base64 `data`, `mime_type` and `filename`).
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal

from organize.find_config import USER_CONFIG_DIR

Provider = Literal["anthropic", "openai", "gemini"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]
Part = Dict[str, str]

DEFAULT_MODELS: Dict[str, str] = {
    "anthropic": "claude-opus-5-5",
    "openai": "gpt-6.1-sol",
    "gemini": "gemini-3.8-flash",
}

# Models accepting Anthropic's server-side `fallbacks` parameter.
ANTHROPIC_FALLBACK_MODELS = {
    "claude-fable-5-1",
    "claude-opus-5-5",
    "claude-opus-5",
    "claude-sonnet-5-5",
}

# Gemini has fewer thinking levels.
GEMINI_THINKING = {
    "low": "low",
    "medium": "medium",
    "high": "high",
    "xhigh": "high",
    "max": "high",
}

MAX_OUTPUT_TOKENS = 8000


def load_env() -> None:
    # API keys can be stored in a `.env` file in the current directory or the config
    # directory. Variables already set take precedence.
    from dotenv import load_dotenv

    for path in (Path(".env"), USER_CONFIG_DIR / ".env"):
        if path.is_file():
            load_dotenv(path, override=False)


class AnswerError(ValueError):
    pass


def is_invalid_input(e: Exception) -> bool:
    """Whether the provider rejected the request, e.g. because of an invalid file."""
    # all three SDKs set the HTTP status on their errors
    return getattr(e, "status_code", None) == 400


@lru_cache(maxsize=None)
def get_client(provider: Provider):
    load_env()
    if provider == "anthropic":
        import anthropic

        return anthropic.Anthropic()
    elif provider == "openai":
        import openai

        return openai.OpenAI()
    elif provider == "gemini":
        from google import genai

        return genai.Client()
    raise ValueError(f"Unknown provider {provider}")


def ask(
    provider: Provider,
    model: str,
    effort: Effort,
    system: str,
    schema: Dict[str, Any],
    parts: List[Part],
) -> str:
    """Returns the JSON text of the answer."""
    if provider == "anthropic":
        return _ask_anthropic(model, effort, system, schema, parts)
    elif provider == "openai":
        return _ask_openai(model, effort, system, schema, parts)
    elif provider == "gemini":
        return _ask_gemini(model, effort, system, schema, parts)
    raise ValueError(f"Unknown provider {provider}")


def _ask_anthropic(model, effort, system, schema, parts) -> str:
    content: List[Dict[str, Any]] = []
    for part in parts:
        if part["kind"] == "text":
            content.append({"type": "text", "text": part["text"]})
        else:
            content.append(
                {
                    "type": "image" if part["kind"] == "image" else "document",
                    "source": {
                        "type": "base64",
                        "media_type": part["mime_type"],
                        "data": part["data"],
                    },
                }
            )
    kwargs: Dict[str, Any] = dict(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system,
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": schema},
        },
        messages=[{"role": "user", "content": content}],
    )
    client = get_client("anthropic")
    if model in ANTHROPIC_FALLBACK_MODELS:
        # retry a declined request on Anthropic's recommended fallback model
        response = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **kwargs,
        )
    else:
        response = client.messages.create(**kwargs)

    if response.stop_reason == "refusal":
        raise AnswerError("Claude declined to answer")
    if response.stop_reason == "max_tokens":
        raise AnswerError("The answer was cut off")
    texts = [b.text for b in response.content if b.type == "text"]
    if not texts:
        raise AnswerError("No answer")
    return texts[-1]


def _ask_openai(model, effort, system, schema, parts) -> str:
    content: List[Dict[str, Any]] = []
    for part in parts:
        if part["kind"] == "text":
            content.append({"type": "input_text", "text": part["text"]})
        elif part["kind"] == "image":
            url = f"data:{part['mime_type']};base64,{part['data']}"
            content.append({"type": "input_image", "image_url": url})
        else:
            content.append(
                {
                    "type": "input_file",
                    "filename": part["filename"],
                    "file_data": f"data:{part['mime_type']};base64,{part['data']}",
                }
            )
    response = get_client("openai").responses.create(
        model=model,
        instructions=system,
        input=[{"role": "user", "content": content}],
        reasoning={"effort": effort},
        max_output_tokens=MAX_OUTPUT_TOKENS,
        text={
            "format": {
                "type": "json_schema",
                "name": "classification",
                "schema": schema,
                "strict": True,
            }
        },
    )
    if response.status != "completed":
        raise AnswerError(f"The answer is {response.status}")
    if not response.output_text:
        raise AnswerError("No answer (the model may have declined)")
    return response.output_text


def _ask_gemini(model, effort, system, schema, parts) -> str:
    content: List[Dict[str, Any]] = []
    for part in parts:
        if part["kind"] == "text":
            content.append({"type": "text", "text": part["text"]})
        else:
            content.append(
                {
                    "type": "image" if part["kind"] == "image" else "document",
                    "data": part["data"],
                    "mime_type": part["mime_type"],
                }
            )
    interaction = get_client("gemini").interactions.create(
        model=model,
        system_instruction=system,
        input=content,
        store=False,
        generation_config={
            "thinking_level": GEMINI_THINKING[effort],
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        },
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": schema,
        },
    )
    if interaction.status != "completed":
        raise AnswerError(f"The answer is {interaction.status}")
    if not interaction.output_text:
        raise AnswerError("No answer")
    return interaction.output_text
