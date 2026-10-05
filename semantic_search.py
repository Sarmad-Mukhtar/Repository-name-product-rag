from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


ELASTICSEARCH_URL = "http://localhost:9201"
INDEX_NAME = "products_vendor_improve_rag_semantic"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


model = SentenceTransformer(MODEL_NAME)

es = Elasticsearch(ELASTICSEARCH_URL)


def semantic_search(query: str, size: int = 5):
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    response = es.search(
        index=INDEX_NAME,
        knn={
            "field": "embedding",
            "query_vector": query_embedding,
            "k": size,
            "num_candidates": 50,
        },
        size=size,
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
    query = input("Semantic search: ")

    results = semantic_search(query)

    print("\nSemantic Search Results:\n")

    for index, product in enumerate(results, start=1):
        print(f"{index}. {product['name']}")
        print(f"   ID: {product['id']}")
        print(f"   Manufacturer: {product['manufacturer']}")
        print(f"   Category: {product['category']}")
        print(f"   Price: {product['price']}")
        print(f"   Semantic Score: {product['score']}")
        print()
