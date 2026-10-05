from rag.pipeline import answer_with_rag


def run_test(test_number, question):
    print(f"\n{'=' * 70}")
    print(f"TEST {test_number}")
    print(f"QUESTION: {question}")
    print("=" * 70)

    result = answer_with_rag(question)

    print("\nANSWER:")
    print(result["answer"])

    print(f"\nPRODUCTS RETRIEVED: {len(result['products'])}")

    for product in result["products"]:
        print(
            f"- {product['name']} "
            f"| Price: {product['price']} "
            f"| Score: {product['score']}"
        )

    return result


def test_exact_product_is_top_result():
    result = answer_with_rag(
        "What is the price of the CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT?"
    )

    assert len(result["products"]) > 0

    top_product = result["products"][0]

    assert (
        top_product["name"]
        == "CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT"
    )

    assert top_product["price"] == 8409.19

    print("\nExact product retrieval validation passed!")


def main():
    run_test(
        1,
        "What is the price of the CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT?",
    )

    run_test(
        2,
        "Who manufactures the CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT?",
    )

    run_test(
        3,
        "What category does the CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT belong to?",
    )

    run_test(
        4,
        "Tell me about a wireless networking product.",
    )

    run_test(
        5,
        "What is the price of a product that does not exist in our data?",
    )

    # Strict retrieval validation
    test_exact_product_is_top_result()


if __name__ == "__main__":
    main()
