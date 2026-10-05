from elasticsearch import Elasticsearch



ELASTICSEARCH_URL = "http://localhost:9201"
INDEX_NAME = "products_vendor_improve_rag"

es = Elasticsearch(ELASTICSEARCH_URL)


def search_products(query: str, size: int = 5):
    response = es.search(
        index=INDEX_NAME,
        size=size,
        query={
            "multi_match": {
                "query": query,
                "fields": [
                    "Name",
                    "Description",
                    "ManufacturerName",
                    "Category",
                    "SearchableText",
                    "Specification",
                ],
            }
        },
    )

    results = []

    for hit in response["hits"]["hits"]:
        source = hit["_source"]

        results.append(
            {
                "id": source["Id"],
                "name": source["Name"],
                "manufacturer": source["ManufacturerName"],
                "category": source["Category"],
                "price": source["ListPrice"],
                "score": hit["_score"],
            }
        )

    return results


if __name__ == "__main__":
    query = input("Search: ")

    results = search_products(query)

    print("\nResults:\n")

    for index, product in enumerate(results, start=1):
        print(f"{index}. {product['name']}")
        print(f"   ID: {product['id']}")
        print(f"   Manufacturer: {product['manufacturer']}")
        print(f"   Category: {product['category']}")
        print(f"   Price: {product['price']}")
        print(f"   BM25 Score: {product['score']}")
        print()
