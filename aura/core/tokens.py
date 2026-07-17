from math import ceil

from aura.core.config import CONTEXT_BUDGET


def count_tokens(messages: list[dict[str, str]]) -> int:
    """
    Approximate token count.
    Assumes roughly 1 token ≈ 4 characters.
    """

    total_characters = 0

    for message in messages:
        total_characters += len(message["content"])

    return ceil(total_characters / 4)

def needs_trimming(history: list[dict[str, str]]) -> bool:
    """
    Return True if the conversation exceeds the context budget.
    """

    return count_tokens(history) > CONTEXT_BUDGET