from __future__ import annotations

import json
import math

from google.genai import types

from aura.core.config import DOCS_DIR, EMBED_MODEL, INDEX_PATH
from aura.core.llm_client import client

EMBED_DIM = 768
MIN_SCORE = 0.6

_index: list[dict] | None = None


class RetrievalError(Exception):
    "Raised when there is nothing to search."


def embed(texts: list[str], task: str) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task,
            output_dimensionality=EMBED_DIM,
        ),
    )

    return [item.values for item in response.embeddings]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    left = math.sqrt(sum(x * x for x in a))
    right = math.sqrt(sum(x * x for x in b))

    if left == 0 or right == 0:
        return 0.0

    return dot / (left * right)


def split_into_chunks(text: str) -> list[str]:
    chunks = []

    for block in text.split("\n\n"):
        block = " ".join(block.split())

        if len(block.split()) > 8:
            chunks.append(block)

    return chunks


def build_index() -> int:
    global _index

    entries = []

    for path in sorted(DOCS_DIR.glob("*.txt")):
        for chunk in split_into_chunks(path.read_text(encoding="utf-8")):
            entries.append({"source": path.name, "text": chunk})

    if not entries:
        raise RetrievalError(f"no .txt files to index in {DOCS_DIR}")

    for entry, vector in zip(entries, embed([e["text"] for e in entries], "RETRIEVAL_DOCUMENT")):
        entry["embedding"] = vector

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(entries), encoding="utf-8")

    _index = entries
    return len(entries)


def is_stale() -> bool:
    if not INDEX_PATH.exists():
        return True

    built_at = INDEX_PATH.stat().st_mtime
    return any(path.stat().st_mtime > built_at for path in DOCS_DIR.glob("*.txt"))


def load_index() -> list[dict]:
    global _index

    if is_stale():
        build_index()
    elif _index is None:
        _index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    return _index


def search_notes(query: str, k: int = 3) -> str:
    """Top matching chunks from the local notes, formatted for the model to read."""

    query_vector = embed([query], "RETRIEVAL_QUERY")[0]

    ranked = sorted(
        ((cosine(query_vector, entry["embedding"]), entry) for entry in load_index()),
        key=lambda pair: pair[0],
        reverse=True,
    )

    hits = [(score, entry) for score, entry in ranked[:k] if score >= MIN_SCORE]

    if not hits:
        return "Nothing in the notes covers that."

    return "\n\n".join(
        f"{entry['source']} (match {score:.2f})\n{entry['text']}" for score, entry in hits
    )


if __name__ == "__main__":
    print(f"indexed {build_index()} chunks into {INDEX_PATH}")
