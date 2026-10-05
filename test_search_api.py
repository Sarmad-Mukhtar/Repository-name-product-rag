import requests


BASE_URL = "http://127.0.0.1:8000"

EXACT_PRODUCT = (
    "CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT"
)

EXPECTED_MANUFACTURER = "CISCO SYSTEMS"
EXPECTED_PRICE = 8409.19


def test_mapping():
    response = requests.get(
        f"{BASE_URL}/mapping"
    )

    assert response.status_code == 200

    data = response.json()

    assert "products_vendor_improve_rag" in data

    mapping = data["products_vendor_improve_rag"]["mappings"]

    assert "properties" in mapping

    properties = mapping["properties"]

    assert "Name" in properties
    assert "Description" in properties
    assert "ManufacturerName" in properties
    assert "Category" in properties
    assert "ListPrice" in properties

    assert properties["Name"]["type"] == "text"
    assert properties["Description"]["type"] == "text"
    assert properties["ListPrice"]["type"] == "double"

    print("[PASS] GET /mapping")


def test_bm25_search():
    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "q": "wireless networking",
            "size": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "wireless networking"
    assert len(data["results"]) == 5

    for product in data["results"]:
        assert "id" in product
        assert "name" in product
        assert "manufacturer" in product
        assert "category" in product
        assert "price" in product
        assert "score" in product

    print("[PASS] GET /search BM25")


def test_exact_product_search():
    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "q": EXACT_PRODUCT,
            "size": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == EXACT_PRODUCT
    assert len(data["results"]) > 0

    top_product = data["results"][0]

    assert top_product["name"] == EXACT_PRODUCT
    assert (
        top_product["manufacturer"]
        == EXPECTED_MANUFACTURER
    )
    assert top_product["price"] == EXPECTED_PRICE

    print("[PASS] GET /search exact product")


def test_search_size():
    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "q": "wireless",
            "size": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["results"]) == 3

    print("[PASS] GET /search size parameter")


if __name__ == "__main__":
    print("=" * 60)
    print("SEARCH API VALIDATION")
    print("=" * 60)

    test_mapping()
    test_bm25_search()
    test_exact_product_search()
    test_search_size()

    print("=" * 60)
    print("ALL SEARCH API TESTS PASSED")
    print("=" * 60)
