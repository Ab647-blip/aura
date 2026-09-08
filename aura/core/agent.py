from __future__ import annotations

import time

from google.genai import types

from aura.core.config import MAX_TOKENS, MODEL, TEMPERATURE, TOP_K, TOP_P
from aura.core.llm_client import build_contents, client, extract_text, extract_usage
from aura.core.prompts import AURA_SYSTEM_PROMPT, ROUTING_RULES
from aura.core.retrieval import search_notes
from aura.core.web import web_search

SYSTEM = f"{AURA_SYSTEM_PROMPT}\n\n{ROUTING_RULES}"

TOOLS = {
    "search_notes": search_notes,
    "web_search": web_search,
}


def declare(name: str, description: str, argument: str) -> types.FunctionDeclaration:
    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"query": types.Schema(type=types.Type.STRING, description=argument)},
            required=["query"],
        ),
    )


DECLARATIONS = [
    declare(
        "search_notes",
        "Search the user's own notes: meetings, decisions, goals, preferences and admin dates.",
        "What to look for, in the user's own words.",
    ),
    declare(
        "web_search",
        "Search the public web for current facts, news, prices and anything that changes over time.",
        "The search query.",
    ),
]


def settings(with_tools: bool) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=SYSTEM,
        tools=[types.Tool(function_declarations=DECLARATIONS)] if with_tools else None,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        max_output_tokens=MAX_TOKENS,
    )


def run_tool(call) -> tuple[str, float]:
    started = time.perf_counter()

    try:
        output = TOOLS[call.name](**dict(call.args))
    except KeyError:
        output = f"{call.name} is not a tool Aura has."
    except Exception as e:
        output = f"{call.name} failed: {e}"

    return output, time.perf_counter() - started


def respond(history: list[dict[str, str]]) -> dict:
    """Let the model decide between answering directly and calling one of the tools."""

    contents = build_contents(history)
    first = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=settings(with_tools=True),
    )

    calls = first.function_calls or []

    if not calls:
        return {
            "text": extract_text(first),
            "tool": None,
            "query": None,
            "result": None,
            "seconds": 0.0,
            "usage": extract_usage(first),
        }

    call = calls[0]
    output, seconds = run_tool(call)

    contents.append(first.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response={"result": output})],
        )
    )

    final = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=settings(with_tools=False),
    )

    first_usage = extract_usage(first)
    final_usage = extract_usage(final)

    return {
        "text": extract_text(final),
        "tool": call.name,
        "query": dict(call.args).get("query", ""),
        "result": output,
        "seconds": seconds,
        "usage": {
            "input_tokens": first_usage["input_tokens"] + final_usage["input_tokens"],
            "output_tokens": first_usage["output_tokens"] + final_usage["output_tokens"],
        },
    }
