from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


ELASTICSEARCH_URL = "http://localhost:9201"

INDEX_NAME = "products_vendor_improve_rag"
SEMANTIC_INDEX_NAME = "products_vendor_improve_rag_semantic"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# BM25 relevance threshold.
BM25_MIN_SCORE = 5.0

# Semantic relevance threshold.
#
# Previous testing showed:
#
# Legitimate semantic matches:
# approximately 0.70+
#
# False "iPhone 20" matches:
# approximately 0.63 - 0.66
#
# Therefore we reject semantic results below 0.68.
SEMANTIC_MIN_SCORE = 0.68


es = Elasticsearch(ELASTICSEARCH_URL)

semantic_model = SentenceTransformer(MODEL_NAME)


def retrieve_products(query: str, size: int = 5):
    """
    Retrieve products using BM25.

    Exact product-name matches are checked first.

    For short queries with two terms or fewer, every query
    term must exist somewhere across the searchable fields.

    This prevents a query such as:

        iPhone 20

    from matching an unrelated product that only contains:

        20

    Longer natural-language queries use a more flexible
    minimum_should_match rule.
    """

    clean_query = query.strip()

    if not clean_query:
        return []

    # ---------------------------------------------------------
    # Exact product-name match
    # ---------------------------------------------------------

    exact_response = es.search(
        index=INDEX_NAME,
        size=1,
        query={
            "term": {
                "Name.keyword": clean_query,
            }
        },
    )

    exact_hits = exact_response["hits"]["hits"]

    if exact_hits:
        hit = exact_hits[0]
        source = hit["_source"]

        return [
            {
                "id": source["Id"],
                "name": source["Name"],
                "manufacturer": source["ManufacturerName"],
                "category": source["Category"],
                "description": source.get("Description"),
                "price": source["ListPrice"],
                "score": hit["_score"],
            }
        ]

    # ---------------------------------------------------------
    # Searchable fields
    # ---------------------------------------------------------

    searchable_fields = [
        "Name",
        "Description",
        "ManufacturerName",
        "Category",
        "SearchableText",
        "Specification",
    ]

    # ---------------------------------------------------------
    # Count query terms
    # ---------------------------------------------------------

    query_terms = clean_query.split()
    term_count = len(query_terms)

    # ---------------------------------------------------------
    # Short query
    #
    # Example:
    #
    #     iPhone 20
    #
    # Every term must match somewhere across the searchable
    # fields.
    # ---------------------------------------------------------

    if term_count <= 2:
        response = es.search(
            index=INDEX_NAME,
            size=size,
            min_score=BM25_MIN_SCORE,
            query={
                "multi_match": {
                    "query": clean_query,
                    "fields": searchable_fields,
                    "type": "cross_fields",
                    "operator": "and",
                }
            },
        )

    # ---------------------------------------------------------
    # Medium / long query
    #
    # Natural-language queries can contain words that do not
    # literally appear in every product document, so we use
    # a more flexible matching rule.
    # ---------------------------------------------------------

    else:
        if term_count <= 4:
            minimum_should_match = "75%"
        else:
            minimum_should_match = "50%"

        response = es.search(
            index=INDEX_NAME,
            size=size,
            min_score=BM25_MIN_SCORE,
            query={
                "multi_match": {
                    "query": clean_query,
                    "fields": searchable_fields,
                    "type": "best_fields",
                    "minimum_should_match": minimum_should_match,
                }
            },
        )

    # ---------------------------------------------------------
    # Convert Elasticsearch results
    # ---------------------------------------------------------

    products = []

    for hit in response["hits"]["hits"]:
        source = hit["_source"]

        products.append(
            {
                "id": source["Id"],
                "name": source["Name"],
                "manufacturer": source["ManufacturerName"],
                "category": source["Category"],
                "description": source.get("Description"),
                "price": source["ListPrice"],
                "score": hit["_score"],
            }
        )

    return products


def retrieve_semantic_products(query: str, size: int = 5):
    """
    Retrieve products using semantic vector search.

    Only results with a semantic score of at least
    SEMANTIC_MIN_SCORE are accepted.
    """

    clean_query = query.strip()

    if not clean_query:
        return []

    query_embedding = semantic_model.encode(
        clean_query,
        normalize_embeddings=True,
    ).tolist()

    response = es.search(
        index=SEMANTIC_INDEX_NAME,
        knn={
            "field": "embedding",
            "query_vector": query_embedding,
            "k": size,
            "num_candidates": 50,
        },
        size=size,
        min_score=SEMANTIC_MIN_SCORE,
    )

    products = []

    for hit in response["hits"]["hits"]:
        source = hit["_source"]

        products.append(
            {
                "id": source["Id"],
                "name": source["Name"],
                "manufacturer": source["ManufacturerName"],
                "category": source["Category"],
                "description": source.get("Description"),
                "price": source["ListPrice"],
                "score": hit["_score"],
            }
        )

    return products


def retrieve_hybrid_products(query: str, size: int = 5):
    """
    Retrieve products using BM25 + semantic search.

    Only results that pass the individual retrieval
    relevance thresholds participate in RRF.
    """

    clean_query = query.strip()

    if not clean_query:
        return []

    candidate_size = max(size * 2, 10)

    # ---------------------------------------------------------
    # BM25 retrieval
    # ---------------------------------------------------------

    bm25_products = retrieve_products(
        clean_query,
        candidate_size,
    )

    # ---------------------------------------------------------
    # Semantic retrieval
    # ---------------------------------------------------------

    semantic_products = retrieve_semantic_products(
        clean_query,
        candidate_size,
    )

    # ---------------------------------------------------------
    # Reciprocal Rank Fusion
    # ---------------------------------------------------------

    RRF_K = 60

    combined = {}

    # ---------------------------------------------------------
    # Add BM25 results
    # ---------------------------------------------------------

    for rank, product in enumerate(
        bm25_products,
        start=1,
    ):
        product_id = product["id"]

        if product_id not in combined:
            combined[product_id] = {
                **product,
                "rrf_score": 0.0,
            }

        combined[product_id]["rrf_score"] += (
            1.0 / (RRF_K + rank)
        )

    # ---------------------------------------------------------
    # Add semantic results
    # ---------------------------------------------------------

    for rank, product in enumerate(
        semantic_products,
        start=1,
    ):
        product_id = product["id"]

        if product_id not in combined:
            combined[product_id] = {
                **product,
                "rrf_score": 0.0,
            }

        combined[product_id]["rrf_score"] += (
            1.0 / (RRF_K + rank)
        )

    # ---------------------------------------------------------
    # Sort by RRF score
    # ---------------------------------------------------------

    products = list(combined.values())

    products.sort(
        key=lambda product: product["rrf_score"],
        reverse=True,
    )

    # ---------------------------------------------------------
    # Return final products
    # ---------------------------------------------------------

    results = []

    for product in products[:size]:
        product["score"] = product["rrf_score"]

        results.append(product)

    return results


def build_context(products):
    """
    Convert retrieved products into LLM context.
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


def retrieve_context(query: str, size: int = 5):
    """
    Retrieve BM25 products and build context.
    """

    products = retrieve_products(
        query,
        size,
    )

    context = build_context(products)

    return {
        "query": query,
        "products": products,
        "context": context,
    }
