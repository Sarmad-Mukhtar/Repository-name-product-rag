from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from elasticsearch import Elasticsearch

from rag.pipeline import (
    answer_with_rag,
    answer_with_semantic_rag,
    answer_with_hybrid_rag,
)


# ============================================================
# Elasticsearch
# ============================================================

ELASTICSEARCH_URL = "http://localhost:9201"
INDEX_NAME = "products_vendor_improve_rag"
es = Elasticsearch(ELASTICSEARCH_URL)


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="Product RAG API",
    description="BM25, semantic, and hybrid RAG API for product questions",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

# Allow the Next.js frontend to communicate with this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request Models
# ============================================================

class ChatMessage(BaseModel):
    user: str
    assistant: str


class RAGRequest(BaseModel):
    question: str
    size: int = Field(default=5, ge=1, le=50)
    history: list[ChatMessage] = Field(default_factory=list)


# ============================================================
# Basic API
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Product RAG API is running"
    }


# ============================================================
# Elasticsearch Mapping
# ============================================================

@app.get("/mapping")
def mapping():
    """
    Return the Elasticsearch mapping for the BM25 product index.
    """

    response = es.indices.get_mapping(
        index=INDEX_NAME
    )

    return response.body


# ============================================================
# BM25 RAG
# ============================================================

@app.post("/rag")
def rag(request: RAGRequest):
    """
    BM25-based RAG.
    """

    result = answer_with_rag(
        request.question,
        request.size,
        history=[
            message.model_dump()
            for message in request.history
        ],
    )

    return {
        "question": result["query"],
        "search_query": result["search_query"],
        "answer": result["answer"],
        "products": result["products"],
    }


# ============================================================
# Semantic RAG
# ============================================================

@app.post("/rag/semantic")
def semantic_rag(request: RAGRequest):
    """
    Semantic/vector-based RAG.
    """

    result = answer_with_semantic_rag(
        request.question,
        request.size,
        history=[
            message.model_dump()
            for message in request.history
        ],
    )

    return {
        "question": result["query"],
        "search_query": result["search_query"],
        "answer": result["answer"],
        "products": result["products"],
    }


# ============================================================
# Hybrid RAG
# ============================================================

@app.post("/rag/hybrid")
def hybrid_rag(request: RAGRequest):
    """
    Hybrid RAG using both BM25 and semantic search.
    """

    result = answer_with_hybrid_rag(
        request.question,
        request.size,
        history=[
            message.model_dump()
            for message in request.history
        ],
    )

    return {
        "question": result["query"],
        "search_query": result["search_query"],
        "answer": result["answer"],
        "products": result["products"],
    }
