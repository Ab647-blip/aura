from aura.core.llm_client import call_llm

SUMMARY_SYSTEM_PROMPT = """
Summarize the key facts, decisions, and open questions from this conversation in under 150 words.
Preserve any information Aura would need to remember for future conversations.
Do not include unnecessary details.
""".strip()

def summarize_history(history: list[dict[str, str]]) -> str:
    """
    Summarize an older conversation history.
    """

    response = call_llm(
        messages=history,
        system=SUMMARY_SYSTEM_PROMPT,
    )

    return response["text"]

def compress_history(
    history: list[dict[str, str]],
    keep_last_n: int = 6,
) -> list[dict[str, str]]:
    """
    Replace old conversation with a summary while keeping
    the most recent messages unchanged.
    """

    if len(history) <= keep_last_n:
        return history

    old_history = history[:-keep_last_n]
    recent_history = history[-keep_last_n:]

    summary = summarize_history(old_history)

    compressed_history = [
        {
            "role": "user",
            "content": f"[Earlier conversation summary]: {summary}",
        }
    ]

    compressed_history.extend(recent_history)

    return compressed_history