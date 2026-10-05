from rag.retriever import (
    retrieve_products,
    retrieve_semantic_products,
    retrieve_hybrid_products,
    build_context,
)

from rag.llm import (
    generate_answer,
    rewrite_query,
)


def retrieve_for_rag(
    query: str,
    size: int = 5,
    history: list | None = None,
):
    search_query = rewrite_query(query, history)

    products = retrieve_products(
        search_query,
        size,
    )

    context = build_context(products)

    return {
        "query": query,
        "search_query": search_query,
        "products": products,
        "context": context,
    }


def retrieve_for_semantic_rag(
    query: str,
    size: int = 5,
    history: list | None = None,
):
    search_query = rewrite_query(query, history)

    products = retrieve_semantic_products(
        search_query,
        size,
    )

    context = build_context(products)

    return {
        "query": query,
        "search_query": search_query,
        "products": products,
        "context": context,
    }


def retrieve_for_hybrid_rag(
    query: str,
    size: int = 5,
    history: list | None = None,
):
    search_query = rewrite_query(query, history)

    products = retrieve_hybrid_products(
        search_query,
        size,
    )

    context = build_context(products)

    return {
        "query": query,
        "search_query": search_query,
        "products": products,
        "context": context,
    }


def answer_with_rag(
    query: str,
    size: int = 5,
    history: list | None = None,
):
    result = retrieve_for_rag(
        query,
        size,
        history,
    )

    answer = generate_answer(
        question=query,
        context=result["context"],
        history=history,
    )

    return {
        "query": result["query"],
        "search_query": result["search_query"],
        "products": result["products"],
        "context": result["context"],
        "answer": answer,
    }


def answer_with_semantic_rag(
    query: str,
    size: int = 5,
    history: list | None = None,
):
    result = retrieve_for_semantic_rag(
        query,
        size,
        history,
    )

    answer = generate_answer(
        question=query,
        context=result["context"],
        history=history,
    )

    return {
        "query": result["query"],
        "search_query": result["search_query"],
        "products": result["products"],
        "context": result["context"],
        "answer": answer,
    }


def answer_with_hybrid_rag(
    query: str,
    size: int = 5,
    history: list | None = None,
):
    result = retrieve_for_hybrid_rag(
        query,
        size,
        history,
    )

    answer = generate_answer(
        question=query,
        context=result["context"],
        history=history,
    )

    return {
        "query": result["query"],
        "search_query": result["search_query"],
        "products": result["products"],
        "context": result["context"],
        "answer": answer,
    }
