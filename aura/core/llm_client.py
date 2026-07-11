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
    "Raised when Gemini returns an API error."


class APIConnectionError(Exception):
    "Raised when the API cannot be reached."

def _build_contents(messages: list[dict[str, str]]) -> list[types.Content]:
    contents = []

    for message in messages:

        role = "model" if message["role"] == "assistant" else message["role"]

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(text=message["content"])
                ],
            )
        )

    return contents


def _extract_text(response: Any) -> str:
  

    if response.text:
        return response.text

    return ""


def _extract_usage(response: Any) -> dict[str, int]:
   

    usage = getattr(response, "usage_metadata", None)

    if usage is None:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
        }

    return {
        "input_tokens": usage.prompt_token_count,
        "output_tokens": usage.candidates_token_count,
    }



def call_llm(
    messages: list[dict[str, str]],
    system: str = "",
    model: str = MODEL,
    max_tokens: int = MAX_TOKENS,
) -> dict[str, Any]:

    contents = _build_contents(messages)

    config = types.GenerateContentConfig(
        system_instruction=system if system else None,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        max_output_tokens=max_tokens,
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

    except Exception as e:
        raise APIError(f"Gemini API request failed: {e}") from e

    text = _extract_text(response)
    usage = _extract_usage(response)

    return {
        "text": text,
        "raw_response": response,
        "usage": usage,
    }