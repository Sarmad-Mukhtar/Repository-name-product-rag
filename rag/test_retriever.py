from rag.retriever import (
    retrieve_products,
    retrieve_semantic_products,
    build_context,
)


def test_wireless_search_returns_products():
    products = retrieve_products("wireless")

    assert len(products) > 0

    print(f"\nBM25 retrieved {len(products)} products")

    for product in products:
        print(f"- {product['name']}")


def test_context_contains_product_information():
    products = retrieve_products("wireless")
    context = build_context(products)

    assert len(context) > 0
    assert "Product:" in context
    assert "Name:" in context
    assert "Manufacturer:" in context
    assert "Price:" in context

    print("\nBM25 context validation passed!")


def test_semantic_search_returns_products():
    products = retrieve_semantic_products(
        "device for connecting computers without cables"
    )

    assert len(products) > 0

    print(f"\nSemantic search retrieved {len(products)} products")

    for product in products:
        assert product["id"]
        assert product["name"]
        assert product["score"] is not None

        print(
            f"- {product['name']} "
            f"| Semantic Score: {product['score']}"
        )


if __name__ == "__main__":
    test_wireless_search_returns_products()
    test_context_contains_product_information()
    test_semantic_search_returns_products()

    print("\nAll RAG retrieval tests passed!")
