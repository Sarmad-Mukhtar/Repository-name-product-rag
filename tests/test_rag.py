from rag.retriever import (
    retrieve_products,
    retrieve_semantic_products,
    retrieve_hybrid_products,
)

from rag.llm import (
    generate_answer,
    rewrite_query,
)


def print_result(name, passed, details=""):
    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {name}")

    if details:
        print(f"       {details}")


def test_exact_product():
    query = "CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT"

    results = retrieve_products(query, 5)

    passed = (
        len(results) > 0
        and results[0]["name"]
        == "CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT"
    )

    print_result(
        "Exact product retrieval",
        passed,
        (
            results[0]["name"]
            if results
            else "No results"
        ),
    )

    return passed


def test_bm25_search():
    query = "wireless controller"

    results = retrieve_products(query, 5)

    passed = len(results) > 0

    print_result(
        "BM25 retrieval",
        passed,
        f"{len(results)} result(s)",
    )

    return passed


def test_semantic_search():
    query = "device for connecting computers without cables"

    results = retrieve_semantic_products(query, 5)

    passed = len(results) > 0

    print_result(
        "Semantic retrieval",
        passed,
        (
            f"{len(results)} result(s), "
            f"top score={results[0]['score']:.4f}"
            if results
            else "No results"
        ),
    )

    return passed


def test_hybrid_search():
    query = "wireless controller"

    results = retrieve_hybrid_products(query, 5)

    passed = len(results) > 0

    print_result(
        "Hybrid retrieval",
        passed,
        f"{len(results)} result(s)",
    )

    return passed


def test_unknown_product():
    query = "iPhone 20"

    results = retrieve_hybrid_products(query, 5)

    passed = len(results) == 0

    print_result(
        "Unknown product rejection",
        passed,
        (
            "No products returned"
            if passed
            else f"{len(results)} unrelated result(s) returned"
        ),
    )

    return passed


def test_rag_price_answer():
    question = (
        "What is the price of the CISCO 5520 "
        "WIRELESS CONTROLLER WRACK MOUNTING KIT?"
    )

    products = retrieve_hybrid_products(
        question,
        5,
    )

    context = build_test_context(products)

    answer = generate_answer(
        question=question,
        context=context,
    )

    passed = "8409.19" in answer

    print_result(
        "RAG price answer",
        passed,
        answer,
    )

    return passed


def test_rag_manufacturer_answer():
    question = (
        "Who manufactures the CISCO 5520 "
        "WIRELESS CONTROLLER WRACK MOUNTING KIT?"
    )

    products = retrieve_hybrid_products(
        question,
        5,
    )

    context = build_test_context(products)

    answer = generate_answer(
        question=question,
        context=context,
    )

    passed = "CISCO SYSTEMS" in answer.upper()

    print_result(
        "RAG manufacturer answer",
        passed,
        answer,
    )

    return passed


def test_rag_unknown_product():
    question = "Tell me about an iPhone 20"

    products = retrieve_hybrid_products(
        question,
        5,
    )

    context = build_test_context(products)

    answer = generate_answer(
        question=question,
        context=context,
    )

    expected_phrase = (
        "I don't have enough information "
        "in the product data."
    )

    passed = expected_phrase.lower() in answer.lower()

    print_result(
        "RAG unknown product protection",
        passed,
        answer,
    )

    return passed


def test_query_rewriting():
    history = [
        {
            "user": (
                "What is the price of the CISCO 5520 "
                "WIRELESS CONTROLLER WRACK MOUNTING KIT?"
            ),
            "assistant": "The price is $8409.19.",
        }
    ]

    question = "Who manufactures it?"

    rewritten_query = rewrite_query(
        question,
        history,
    )

    expected_product = (
        "CISCO 5520 WIRELESS CONTROLLER "
        "WRACK MOUNTING KIT"
    )

    passed = (
        "cisco" in rewritten_query.lower()
        and "5520" in rewritten_query
    )

    print_result(
        "Query rewriting",
        passed,
        f"Rewritten query: {rewritten_query}",
    )

    return passed


def test_follow_up_question():
    history = [
        {
            "user": (
                "What is the price of the CISCO 5520 "
                "WIRELESS CONTROLLER WRACK MOUNTING KIT?"
            ),
            "assistant": "The price is $8409.19.",
        }
    ]

    question = "Who manufactures it?"

    rewritten_query = rewrite_query(
        question,
        history,
    )

    products = retrieve_hybrid_products(
        rewritten_query,
        5,
    )

    context = build_test_context(products)

    answer = generate_answer(
        question=question,
        context=context,
        history=history,
    )

    passed = "CISCO SYSTEMS" in answer.upper()

    print_result(
        "Follow-up question",
        passed,
        answer,
    )

    return passed


def build_test_context(products):
    """
    Build the same product context format used by the RAG
    pipeline for validation purposes.
    """

    context_parts = []

    for product in products:
        context = (
            "Product:\n"
            f"ID: {product['id']}\n"
            f"Name: {product['name']}\n"
            f"Manufacturer: {product['manufacturer']}\n"
            f"Category: {product['category']}\n"
            f"Description: {product['description']}\n"
            f"Price: {product['price']}\n"
        )

        context_parts.append(context)

    return "\n".join(context_parts)


def main():
    print()
    print("=" * 60)
    print("PRODUCT RAG VALIDATION")
    print("=" * 60)
    print()

    tests = [
        test_exact_product,
        test_bm25_search,
        test_semantic_search,
        test_hybrid_search,
        test_unknown_product,
        test_rag_price_answer,
        test_rag_manufacturer_answer,
        test_rag_unknown_product,
        test_query_rewriting,
        test_follow_up_question,
    ]

    passed_count = 0

    for test in tests:
        try:
            if test():
                passed_count += 1
        except Exception as error:
            print_result(
                test.__name__,
                False,
                str(error),
            )

        print()

    total = len(tests)

    print("=" * 60)
    print(
        f"RESULT: {passed_count}/{total} PASSED"
    )
    print("=" * 60)
    print()

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
