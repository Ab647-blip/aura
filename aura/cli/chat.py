from aura.core.llm_client import call_llm
from aura.core.prompts import AURA_SYSTEM_PROMPT
from aura.core.tokens import needs_trimming, count_tokens
from aura.core.context_manager import compress_history

def run_chat() -> None:
    history: list[dict[str, str]] = []
    total_input_tokens = 0

    history = []

    print("kush amadid to Aura Chat")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        user_input = input("You: ").strip()

        history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        response = call_llm(
            messages=history,
            system=AURA_SYSTEM_PROMPT,
        )
        print(f"Aura: {response['text']}")

        history.append(
            {
                "role": "assistant",
                "content": response["text"],
            }
        )
        history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        if needs_trimming(history):
            print("\n⚠ Context budget exceeded. Compressing history...\n")

            before = count_tokens(history)

            history = compress_history(history)

            after = count_tokens(history)

            print(f"[Compression] Tokens: {before} → {after}")

        total_input_tokens += response["usage"]["input_tokens"]

        print(
            f"[DEBUG] Messages: {len(history)} | "
            f"Total Input Tokens: {total_input_tokens}"
        )

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

if __name__ == "__main__":
    run_chat()
