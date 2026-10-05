import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not configured")


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL_NAME = "openai/gpt-4o-mini"


def generate_answer(
    question: str,
    context: str,
    history: list | None = None,
) -> str:

    history = history or []

    history_text = ""

    if history:
        history_parts = []

        for message in history:
            history_parts.append(
                f"User: {message['user']}\n"
                f"Assistant: {message['assistant']}"
            )

        history_text = "\n\n".join(history_parts)

    prompt = f"""
You are a product assistant.

Answer the user's question using only the product information
provided in the context below.

You may use the conversation history to understand what the
user is referring to, especially for follow-up questions such
as:

- "it"
- "that product"
- "who makes it"
- "what category is it"
- "what is its price"

Do not invent product information.

If the answer cannot be found in the product context, say:

"I don't have enough information in the product data."

Conversation history:
{history_text}

Product context:
{context}

User question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer product questions using the "
                    "provided product context and conversation "
                    "history."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content


def rewrite_query(
    question: str,
    history: list | None = None,
) -> str:

    history = history or []

    # No conversation history means there is nothing to rewrite.
    if not history:
        return question.strip()

    history_parts = []

    for message in history:
        history_parts.append(
            f"User: {message['user']}\n"
            f"Assistant: {message['assistant']}"
        )

    history_text = "\n\n".join(history_parts)

    prompt = f"""
You are a search-query rewriting component for a product
search system.

Rewrite the user's latest question into a standalone search
query that can be used to search a product database.

Use the conversation history to resolve references such as:

- "it"
- "that product"
- "this product"
- "its"
- "who makes it"
- "what category is it"
- "what is its price"

The rewritten query must contain the product or subject that
the user is referring to.

Do not answer the question.

Return ONLY the rewritten search query.

IMPORTANT:
- Do not write "Search query:"
- Do not write "search query:"
- Do not add labels.
- Do not add explanations.
- Do not use quotation marks around the query.

Conversation history:
{history_text}

Latest user question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You rewrite product questions into "
                    "standalone Elasticsearch search queries. "
                    "Return only the query itself."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    rewritten_query = response.choices[0].message.content.strip()

    # ---------------------------------------------------------
    # Defensive cleanup
    # ---------------------------------------------------------
    #
    # Sometimes the model may still return:
    #
    # Search query: "iPhone 20"
    #
    # or:
    #
    # search query: search query: "iPhone 20"
    #
    # Remove repeated "search query:" prefixes.
    # ---------------------------------------------------------

    while rewritten_query.lower().startswith("search query:"):
        rewritten_query = rewritten_query[
            len("search query:")
        ].strip()

    # Remove surrounding quotes if the model added them.
    if (
        len(rewritten_query) >= 2
        and (
            (
                rewritten_query.startswith('"')
                and rewritten_query.endswith('"')
            )
            or (
                rewritten_query.startswith("'")
                and rewritten_query.endswith("'")
            )
        )
    ):
        rewritten_query = rewritten_query[1:-1].strip()

    return rewritten_query
