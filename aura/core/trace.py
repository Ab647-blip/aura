from __future__ import annotations

import json
from datetime import datetime

from aura.core.config import LOG_PATH


def shorten(text: str | None, limit: int) -> str | None:
    if text is None:
        return None

    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[:limit] + "..."


def log_decision(question: str, answer: dict) -> None:
    entry = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "question": shorten(question, 200),
        "decision": answer["tool"] or "direct",
        "reason": answer["reason"],
        "tool_query": answer["query"],
        "tool_result": shorten(answer["result"], 300),
        "tool_seconds": round(answer["tool_seconds"], 3),
        "total_seconds": round(answer["total_seconds"], 3),
        "input_tokens": answer["usage"]["input_tokens"],
        "output_tokens": answer["usage"]["output_tokens"],
        "reply": shorten(answer["text"], 200),
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(json.dumps(entry, ensure_ascii=False) + "\n")


def recent(limit: int = 20) -> list[dict]:
    if not LOG_PATH.exists():
        return []

    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
