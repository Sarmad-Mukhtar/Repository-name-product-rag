import requests


API_URL = "http://127.0.0.1:8001/rag/hybrid"


def ask_product_chatbot(question: str, history: list):
    """
    Send a product question and conversation history
    to the hybrid RAG API.
    """

    response = requests.post(
        API_URL,
        json={
            "question": question,
            "size": 5,
            "history": history,
        },
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    # Store the current conversation turn.
    history.append(
        {
            "user": question,
            "assistant": result["answer"],
        }
    )

    return result


def main():
    print("=" * 70)
    print("PRODUCT RAG CHATBOT")
    print("Type 'exit' to quit.")
    print("=" * 70)

    history = []

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            result = ask_product_chatbot(
                question,
                history,
            )

            print("\nAssistant:")
            print(result["answer"])

        except requests.RequestException as error:
            print(f"\nAPI error: {error}")


if __name__ == "__main__":
    main()
