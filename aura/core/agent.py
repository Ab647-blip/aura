from __future__ import annotations

import time

from google.genai import types

from aura.core.config import MAX_TOKENS, MODEL, TEMPERATURE, TOP_K, TOP_P
from aura.core.llm_client import build_contents, client, extract_text, extract_usage
from aura.core.prompts import AURA_SYSTEM_PROMPT, ROUTING_RULES
from aura.core.retrieval import search_notes
from aura.core.trace import log_decision
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
            properties={
                "query": types.Schema(type=types.Type.STRING, description=argument),
                "reason": types.Schema(
                    type=types.Type.STRING,
                    description="One short sentence on why this tool fits the question.",
                ),
            },
            required=["query", "reason"],
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


def run_tool(name: str, args: dict) -> tuple[str, float]:
    started = time.perf_counter()

    try:
        output = TOOLS[name](**args)
    except KeyError:
        output = f"{name} is not a tool Aura has."
    except Exception as e:
        output = f"{name} failed: {e}"

    return output, time.perf_counter() - started


def answer_from_tool(contents, first, call) -> dict:
    args = dict(call.args)
    reason = args.pop("reason", "")

    output, tool_seconds = run_tool(call.name, args)

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

    spent = extract_usage(first)
    also_spent = extract_usage(final)

    return {
        "text": extract_text(final),
        "tool": call.name,
        "query": args.get("query", ""),
        "reason": reason,
        "result": output,
        "tool_seconds": tool_seconds,
        "usage": {
            "input_tokens": spent["input_tokens"] + also_spent["input_tokens"],
            "output_tokens": spent["output_tokens"] + also_spent["output_tokens"],
        },
    }


def respond(history: list[dict[str, str]]) -> dict:
    """Let the model decide between answering directly and calling one of the tools."""

    started = time.perf_counter()

    contents = build_contents(history)
    first = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=settings(with_tools=True),
    )

    calls = first.function_calls or []

    if calls:
        answer = answer_from_tool(contents, first, calls[0])
    else:
        answer = {
            "text": extract_text(first),
            "tool": None,
            "query": None,
            "reason": None,
            "result": None,
            "tool_seconds": 0.0,
            "usage": extract_usage(first),
        }

    answer["total_seconds"] = time.perf_counter() - started

    log_decision(history[-1]["content"], answer)

    return answer
