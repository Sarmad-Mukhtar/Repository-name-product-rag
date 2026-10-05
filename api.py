from fastapi import FastAPI, Query
from elasticsearch import Elasticsearch

from app_search import search_products


ELASTICSEARCH_URL = "http://localhost:9201"
INDEX_NAME = "products_vendor_improve_rag"

es = Elasticsearch(ELASTICSEARCH_URL)


app = FastAPI(
    title="Product RAG Search API",
    description="BM25 product search API using Elasticsearch",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Product RAG Search API is running"
    }


@app.get("/mapping")
def mapping():
    """
    Return the Elasticsearch mapping for the product index.
    """

    response = es.indices.get_mapping(
        index=INDEX_NAME
    )

    return response.body


@app.get("/search")
def search(
    q: str = Query(..., min_length=1),
    size: int = Query(5, ge=1, le=50),
):
    return {
        "query": q,
        "results": search_products(q, size),
    }
