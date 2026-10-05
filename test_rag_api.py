import requests


BASE_URL = "http://127.0.0.1:8001"

EXACT_PRODUCT = (
    "CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT"
)

EXPECTED_MANUFACTURER = "CISCO SYSTEMS"

EXPECTED_CATEGORY = (
    "Services--Support & Onsite Services--Onsite Field Services"
)

EXPECTED_PRICE = 8409.19


def test_bm25_rag():
    response = requests.post(
        f"{BASE_URL}/rag",
        json={
            "question": (
                "What is the price of the "
                f"{EXACT_PRODUCT}?"
            ),
            "size": 5,
            "history": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"]
    assert data["search_query"]
    assert data["answer"]
    assert len(data["products"]) > 0

    assert (
        data["products"][0]["name"]
        == EXACT_PRODUCT
    )

    assert data["products"][0]["price"] == EXPECTED_PRICE

    print("[PASS] POST /rag")


def test_semantic_rag():
    response = requests.post(
        f"{BASE_URL}/rag/semantic",
        json={
            "question": (
                "device for connecting computers "
                "without cables"
            ),
            "size": 5,
            "history": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"]
    assert data["search_query"]
    assert data["answer"]
    assert len(data["products"]) == 5

    print("[PASS] POST /rag/semantic")


def test_hybrid_rag():
    response = requests.post(
        f"{BASE_URL}/rag/hybrid",
        json={
            "question": (
                "Tell me about a wireless "
                "networking product."
            ),
            "size": 5,
            "history": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"]
    assert data["search_query"]
    assert data["answer"]
    assert len(data["products"]) == 5

    for product in data["products"]:
        assert "score" in product

    print("[PASS] POST /rag/hybrid")


def test_hybrid_follow_up_manufacturer():
    response = requests.post(
        f"{BASE_URL}/rag/hybrid",
        json={
            "question": "Who manufactures it?",
            "size": 5,
            "history": [
                {
                    "user": (
                        f"What is the price of the "
                        f"{EXACT_PRODUCT}?"
                    ),
                    "assistant": (
                        f"The price of the {EXACT_PRODUCT} "
                        f"is ${EXPECTED_PRICE}."
                    ),
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "Who manufactures it?"

    assert data["search_query"]

    assert EXACT_PRODUCT in data["search_query"]

    assert data["answer"]

    assert EXPECTED_MANUFACTURER in data["answer"]

    assert len(data["products"]) > 0

    assert (
        data["products"][0]["name"]
        == EXACT_PRODUCT
    )

    assert (
        data["products"][0]["manufacturer"]
        == EXPECTED_MANUFACTURER
    )

    print("[PASS] POST /rag/hybrid follow-up manufacturer")


def test_hybrid_follow_up_category():
    response = requests.post(
        f"{BASE_URL}/rag/hybrid",
        json={
            "question": "What category is it?",
            "size": 5,
            "history": [
                {
                    "user": (
                        f"What is the price of the "
                        f"{EXACT_PRODUCT}?"
                    ),
                    "assistant": (
                        f"The price of the {EXACT_PRODUCT} "
                        f"is ${EXPECTED_PRICE}."
                    ),
                },
                {
                    "user": "Who manufactures it?",
                    "assistant": (
                        f"The {EXACT_PRODUCT} is "
                        f"manufactured by "
                        f"{EXPECTED_MANUFACTURER}."
                    ),
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What category is it?"

    assert data["search_query"]

    assert EXACT_PRODUCT in data["search_query"]

    assert data["answer"]

    assert EXPECTED_CATEGORY in data["answer"]

    assert len(data["products"]) > 0

    assert (
        data["products"][0]["name"]
        == EXACT_PRODUCT
    )

    assert (
        data["products"][0]["category"]
        == EXPECTED_CATEGORY
    )

    print("[PASS] POST /rag/hybrid follow-up category")


def test_hybrid_follow_up_price():
    response = requests.post(
        f"{BASE_URL}/rag/hybrid",
        json={
            "question": "What is its price?",
            "size": 5,
            "history": [
                {
                    "user": (
                        f"Tell me about the "
                        f"{EXACT_PRODUCT}."
                    ),
                    "assistant": (
                        f"The {EXACT_PRODUCT} is "
                        f"manufactured by "
                        f"{EXPECTED_MANUFACTURER}."
                    ),
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is its price?"

    assert data["search_query"]

    assert EXACT_PRODUCT in data["search_query"]

    assert data["answer"]

    assert str(EXPECTED_PRICE) in data["answer"]

    assert len(data["products"]) > 0

    assert (
        data["products"][0]["name"]
        == EXACT_PRODUCT
    )

    assert (
        data["products"][0]["price"]
        == EXPECTED_PRICE
    )

    print("[PASS] POST /rag/hybrid follow-up price")


if __name__ == "__main__":
    print("=" * 60)
    print("RAG API VALIDATION")
    print("=" * 60)

    test_bm25_rag()
    test_semantic_rag()
    test_hybrid_rag()

    test_hybrid_follow_up_manufacturer()
    test_hybrid_follow_up_category()
    test_hybrid_follow_up_price()

    print("=" * 60)
    print("ALL RAG API TESTS PASSED")
    print("=" * 60)
