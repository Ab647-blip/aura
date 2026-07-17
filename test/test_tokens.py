from aura.core.tokens import count_tokens, needs_trimming


def test_empty_history():
    history = []

    assert count_tokens(history) == 0
    assert needs_trimming(history) is False


def test_small_history():
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]

    assert count_tokens(history) > 0
    assert needs_trimming(history) is False


def test_large_history():
    history = []

    for _ in range(500):
        history.append(
            {
                "role": "user",
                "content": "This is a long message used for testing token counting.",
            }
        )

    assert needs_trimming(history) is True