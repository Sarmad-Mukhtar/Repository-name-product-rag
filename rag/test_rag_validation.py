from rag.pipeline import (
    answer_with_rag,
    answer_with_semantic_rag,
    answer_with_hybrid_rag,
)


EXACT_PRODUCT = (
    "CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT"
)

EXPECTED_MANUFACTURER = "CISCO SYSTEMS"

EXPECTED_CATEGORY = (
    "Services--Support & Onsite Services--Onsite Field Services"
)

EXPECTED_PRICE = 8409.19


def test_exact_product():
    result = answer_with_rag(
        f"What is the price of the {EXACT_PRODUCT}?"
    )

    assert len(result["products"]) > 0

    top_product = result["products"][0]

    assert top_product["name"] == EXACT_PRODUCT
    assert top_product["price"] == EXPECTED_PRICE

    print("\n[PASS] Exact product lookup")
    print(f"Product: {top_product['name']}")
    print(f"Price: {top_product['price']}")


def test_bm25_search():
    result = answer_with_rag(
        "wireless networking product"
    )

    assert len(result["products"]) > 0

    print("\n[PASS] BM25 retrieval")
    print(f"Retrieved: {len(result['products'])} products")


def test_semantic_search():
    result = answer_with_semantic_rag(
        "device for connecting computers without cables"
    )

    assert len(result["products"]) > 0

    print("\n[PASS] Semantic retrieval")
    print(f"Retrieved: {len(result['products'])} products")


def test_hybrid_search():
    result = answer_with_hybrid_rag(
        "wireless networking product"
    )

    assert len(result["products"]) > 0

    print("\n[PASS] Hybrid RRF retrieval")
    print(f"Retrieved: {len(result['products'])} products")

    for product in result["products"]:
        assert "score" in product


def test_price_question():
    result = answer_with_hybrid_rag(
        f"What is the price of the {EXACT_PRODUCT}?"
    )

    assert len(result["products"]) > 0
    assert result["products"][0]["price"] == EXPECTED_PRICE

    print("\n[PASS] Price question")
    print(result["answer"])


def test_manufacturer_question():
    result = answer_with_hybrid_rag(
        f"Who manufactures the {EXACT_PRODUCT}?"
    )

    assert len(result["products"]) > 0
    assert result["products"][0]["manufacturer"] == EXPECTED_MANUFACTURER

    print("\n[PASS] Manufacturer question")
    print(result["answer"])


def test_category_question():
    result = answer_with_hybrid_rag(
        f"What category does the {EXACT_PRODUCT} belong to?"
    )

    assert len(result["products"]) > 0

    assert (
        result["products"][0]["category"]
        == EXPECTED_CATEGORY
    )

    print("\n[PASS] Category question")
    print(result["answer"])


def test_nonexistent_product():
    result = answer_with_hybrid_rag(
        "What is the price of the XYZ NONEXISTENT PRODUCT 999999?"
    )

    assert (
        "I don't have enough information in the product data."
        in result["answer"]
    )

    print("\n[PASS] Nonexistent product handling")
    print(result["answer"])


def test_answer_generation():
    result = answer_with_hybrid_rag(
        "Tell me about a wireless networking product."
    )

    assert result["answer"]
    assert len(result["answer"]) > 0
    assert len(result["products"]) > 0

    print("\n[PASS] RAG answer generation")
    print(result["answer"])


# ============================================================
# CONVERSATION / FOLLOW-UP TESTS
# ============================================================


def test_follow_up_manufacturer():
    history = [
        {
            "user": (
                f"What is the price of the {EXACT_PRODUCT}?"
            ),
            "assistant": (
                f"The price of the {EXACT_PRODUCT} "
                f"is ${EXPECTED_PRICE}."
            ),
        }
    ]

    result = answer_with_hybrid_rag(
        "Who manufactures it?",
        history=history,
    )

    assert len(result["products"]) > 0

    top_product = result["products"][0]

    assert top_product["name"] == EXACT_PRODUCT
    assert top_product["manufacturer"] == EXPECTED_MANUFACTURER

    assert EXPECTED_MANUFACTURER in result["answer"]

    assert EXACT_PRODUCT in result["search_query"]

    print("\n[PASS] Follow-up manufacturer question")
    print(f"Search query: {result['search_query']}")
    print(result["answer"])


def test_follow_up_category():
    history = [
        {
            "user": (
                f"What is the price of the {EXACT_PRODUCT}?"
            ),
            "assistant": (
                f"The price of the {EXACT_PRODUCT} "
                f"is ${EXPECTED_PRICE}."
            ),
        },
        {
            "user": "Who manufactures it?",
            "assistant": (
                f"The {EXACT_PRODUCT} is manufactured "
                f"by {EXPECTED_MANUFACTURER}."
            ),
        },
    ]

    result = answer_with_hybrid_rag(
        "What category is it?",
        history=history,
    )

    assert len(result["products"]) > 0

    top_product = result["products"][0]

    assert top_product["name"] == EXACT_PRODUCT
    assert top_product["category"] == EXPECTED_CATEGORY

    assert EXPECTED_CATEGORY in result["answer"]

    assert EXACT_PRODUCT in result["search_query"]

    print("\n[PASS] Follow-up category question")
    print(f"Search query: {result['search_query']}")
    print(result["answer"])


def test_follow_up_price():
    history = [
        {
            "user": (
                f"Tell me about the {EXACT_PRODUCT}."
            ),
            "assistant": (
                f"The {EXACT_PRODUCT} is manufactured "
                f"by {EXPECTED_MANUFACTURER}."
            ),
        }
    ]

    result = answer_with_hybrid_rag(
        "What is its price?",
        history=history,
    )

    assert len(result["products"]) > 0

    top_product = result["products"][0]

    assert top_product["name"] == EXACT_PRODUCT
    assert top_product["price"] == EXPECTED_PRICE

    assert str(EXPECTED_PRICE) in result["answer"]

    assert EXACT_PRODUCT in result["search_query"]

    print("\n[PASS] Follow-up price question")
    print(f"Search query: {result['search_query']}")
    print(result["answer"])


if __name__ == "__main__":
    print("=" * 70)
    print("RAG VALIDATION TEST SUITE")
    print("=" * 70)

    # Original RAG tests
    test_exact_product()
    test_bm25_search()
    test_semantic_search()
    test_hybrid_search()
    test_price_question()
    test_manufacturer_question()
    test_category_question()
    test_nonexistent_product()
    test_answer_generation()

    # Conversation / follow-up tests
    test_follow_up_manufacturer()
    test_follow_up_category()
    test_follow_up_price()

    print("\n" + "=" * 70)
    print("ALL RAG VALIDATION TESTS PASSED")
    print("=" * 70)
