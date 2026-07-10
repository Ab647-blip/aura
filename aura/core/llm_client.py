from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

from aura.core.config import (
    API_KEY,
    MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    TOP_P,
    TOP_K,
)


client = genai.Client(api_key=API_KEY)

class APIError(Exception):
    """Raised when Gemini returns an API error."""
class APIConnectionError(Exception):
    """Raised when the API cannot be reached."""


def call_llm(
    messages: list[dict[str, str]],
    system: str = "",
    model: str = MODEL,
    max_tokens: int = MAX_TOKENS,
) -> dict[str, Any]:







