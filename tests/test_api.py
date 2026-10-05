import requests


API_URL = "http://127.0.0.1:8001"


def print_result(name, passed, details=""):
    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {name}")

    if details:
        print(f"       {details}")


def test_root():
    response = requests.get(
        f"{API_URL}/",
        timeout=30,
    )

    passed = (
        response.status_code == 200
        and response.json().get("message")
        == "Product RAG API is running"
    )

    print_result(
        "API root",
        passed,
        f"HTTP {response.status_code}",
    )

    return passed


def test_hybrid_product_question():
    response = requests.post(
        f"{API_URL}/rag/hybrid",
        json={
            "question": (
                "What is the price of the CISCO 5520 "
                "WIRELESS CONTROLLER WRACK MOUNTING KIT?"
            ),
            "size": 5,
            "history": [],
        },
        timeout=120,
    )

    data = response.json()

    passed = (
        response.status_code == 200
        and "answer" in data
        and "products" in data
        and "search_query" in data
        and "8409.19" in data["answer"]
    )

    print_result(
        "Hybrid product question",
        passed,
        (
            f"HTTP {response.status_code} | "
            f"Answer: {data.get('answer')}"
        ),
    )

    return passed


def test_semantic_question():
    response = requests.post(
        f"{API_URL}/rag/semantic",
        json={
            "question": (
                "device for connecting computers "
                "without cables"
            ),
            "size": 5,
            "history": [],
        },
        timeout=120,
    )

    data = response.json()

    passed = (
        response.status_code == 200
        and "answer" in data
        and "products" in data
        and len(data["products"]) > 0
    )

    print_result(
        "Semantic API question",
        passed,
        (
            f"HTTP {response.status_code} | "
            f"{len(data.get('products', []))} product(s)"
        ),
    )

    return passed


def test_bm25_question():
    response = requests.post(
        f"{API_URL}/rag",
        json={
            "question": "wireless controller",
            "size": 5,
            "history": [],
        },
        timeout=120,
    )

    data = response.json()

    passed = (
        response.status_code == 200
        and "answer" in data
        and "products" in data
        and len(data["products"]) > 0
    )

    print_result(
        "BM25 RAG API question",
        passed,
        (
            f"HTTP {response.status_code} | "
            f"{len(data.get('products', []))} product(s)"
        ),
    )

    return passed


def test_unknown_product():
    response = requests.post(
        f"{API_URL}/rag/hybrid",
        json={
            "question": "Tell me about an iPhone 20",
            "size": 5,
            "history": [],
        },
        timeout=120,
    )

    data = response.json()

    expected = (
        "I don't have enough information "
        "in the product data."
    )

    passed = (
        response.status_code == 200
        and expected.lower() in data["answer"].lower()
        and len(data["products"]) == 0
    )

    print_result(
        "Unknown product API protection",
        passed,
        (
            f"HTTP {response.status_code} | "
            f"Products: {len(data.get('products', []))} | "
            f"Answer: {data.get('answer')}"
        ),
    )

    return passed


def test_follow_up_question():
    history = [
        {
            "user": (
                "What is the price of the CISCO 5520 "
                "WIRELESS CONTROLLER WRACK MOUNTING KIT?"
            ),
            "assistant": (
                "The price of the CISCO 5520 "
                "WIRELESS CONTROLLER WRACK MOUNTING KIT "
                "is 8409.19."
            ),
        }
    ]

    response = requests.post(
        f"{API_URL}/rag/hybrid",
        json={
            "question": "Who manufactures it?",
            "size": 5,
            "history": history,
        },
        timeout=120,
    )

    data = response.json()

    passed = (
        response.status_code == 200
        and "CISCO SYSTEMS" in data["answer"].upper()
        and len(data["products"]) > 0
    )

    print_result(
        "Follow-up conversation API",
        passed,
        (
            f"HTTP {response.status_code} | "
            f"Answer: {data.get('answer')}"
        ),
    )

    return passed


def main():
    print()
    print("=" * 60)
    print("PRODUCT RAG API VALIDATION")
    print("=" * 60)
    print()

    tests = [
        test_root,
        test_hybrid_product_question,
        test_semantic_question,
        test_bm25_question,
        test_unknown_product,
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
