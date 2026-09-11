from aura.core.agent import respond
from aura.core.context_manager import compress_history
from aura.core.tokens import count_tokens, needs_trimming


def run_chat() -> None:
    history: list[dict[str, str]] = []
    total_input_tokens = 0

    print("kush amadid to Aura Chat")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        answer = respond(history)

        print(f"Aura: {answer['text']}")

        if answer["tool"]:
            print(f"[{answer['tool']} in {answer['tool_seconds']:.1f}s]")

        history.append(
            {
                "role": "assistant",
                "content": answer["text"],
            }
        )

        if needs_trimming(history):
            print("\n⚠ Context budget exceeded. Compressing history...\n")

            before = count_tokens(history)

            history = compress_history(history)

            after = count_tokens(history)

            print(f"[Compression] Tokens: {before} → {after}")

        total_input_tokens += answer["usage"]["input_tokens"]

        print(
            f"[DEBUG] Messages: {len(history)} | "
            f"Total Input Tokens: {total_input_tokens}"
        )


if __name__ == "__main__":
    run_chat()
