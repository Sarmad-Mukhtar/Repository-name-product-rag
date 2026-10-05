import os

import psycopg
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer


DATABASE_URL = os.environ["PRODUCT_RAG_DATABASE_URL"]

ELASTICSEARCH_URL = "http://localhost:9201"
INDEX_NAME = "products_vendor_improve_rag_semantic"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def build_product_text(product):
    parts = [
        product["name"],
        product["manufacturer_name"],
        product["category"],
        product["description"],
        product["searchable_text"],
        product["specification"],
    ]

    return " ".join(
        str(part)
        for part in parts
        if part
    )


def main():
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded.")

    es = Elasticsearch(ELASTICSEARCH_URL)

    if not es.ping():
        raise RuntimeError(
            f"Could not connect to Elasticsearch at {ELASTICSEARCH_URL}"
        )

    print("Connected to Chatbot #2 Elasticsearch.")

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    manufacturer_name,
                    category,
                    searchable_text,
                    specification,
                    list_price
                FROM products
                """
            )

            rows = cursor.fetchall()

    print(f"Products loaded from PostgreSQL: {len(rows)}")

    products = []

    for row in rows:
        products.append(
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "manufacturer_name": row[3],
                "category": row[4],
                "searchable_text": row[5],
                "specification": row[6],
                "list_price": row[7],
            }
        )

    texts = [
        build_product_text(product)
        for product in products
    ]

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    print("Embeddings generated.")

    actions = []

    for product, embedding in zip(products, embeddings):
        document = {
            "Id": product["id"],
            "Name": product["name"],
            "Description": product["description"],
            "ManufacturerName": product["manufacturer_name"],
            "Category": product["category"],
            "SearchableText": product["searchable_text"],
            "Specification": product["specification"],
            "ListPrice": product["list_price"],
            "embedding": embedding.tolist(),
        }

        actions.append(
            {
                "_index": INDEX_NAME,
                "_id": product["id"],
                "_source": document,
            }
        )

    success, errors = helpers.bulk(
        es,
        actions,
        raise_on_error=False,
    )

    print(f"Successfully indexed: {success}")

    if errors:
        print(f"Indexing errors: {len(errors)}")

        for error in errors[:5]:
            print(error)
    else:
        print("No indexing errors.")


if __name__ == "__main__":
    main()
