# Product RAG Chatbot

A product search and RAG chatbot built using a 500-product dataset.

## 1. Project Overview

The project provides:

- PostgreSQL product storage
- Elasticsearch product indexing
- BM25 keyword search
- Semantic/vector search
- Hybrid search using RRF
- Query rewriting for follow-up questions
- Conversation history
- RAG-based answers
- FastAPI APIs
- Command-line chatbot
- Automated validation tests

---

## 2. Architecture

```text
500 Product Dataset
        |
        v
   PostgreSQL
        |
        v
   Elasticsearch
     /       \
    /         \
 BM25       Semantic
 Search       Search
    \         /
     \       /
      Hybrid RRF
          |
          v
    Query Rewriting
          |
          v
     RAG Retrieval
          |
          v
         LLM
          |
          v
      FastAPI
          |
          v
       Chatbot
       
       
      
3. Dataset
The project uses a 500-product dataset supplied as:
data/products_500_backup.txt

The source file is an Elasticsearch search response containing 500 product documents.

The product data includes fields such as:

Id
Name
Description
ManufacturerName
Category
CategoryId
ListPrice
RegularCost
Quantity
StockStatus
Specification
Specifications
SearchableText
Images
VendorInfo
CategoryPath
ValidationFlags
and other product attributes

4. PostgreSQL
PostgreSQL is used as the structured product data store.
Database:
product_rag
The imported product count is:
500
The PostgreSQL table is:
products
The table stores normalized product fields together with the original product data in raw_data.

5. Elasticsearch
Chatbot #2 uses a dedicated Elasticsearch instance.
Elasticsearch:
http://localhost:9201
This is intentionally separated from the existing Chatbot #1 Elasticsearch instance.
BM25 index
products_vendor_improve_rag
The BM25 index contains the 500 products.
Important searchable fields include:

Name
Description
ManufacturerName
Category
SearchableText
Specification

Semantic index
products_vendor_improve_rag_semantic
The semantic index contains:
Product information
384-dimensional embeddings
Embeddings generated using:
sentence-transformers/all-MiniLM-L6-v2
The vector field uses cosine similarity.

6. BM25 Search
BM25 search is implemented using Elasticsearch.
The search checks product fields including:

Name
Description
ManufacturerName
Category
SearchableText
Specification

Exact product-name lookup is also supported by the RAG retriever.
Example query:
wireless networking
The search API exposes BM25 search through:
GET /search

7. Semantic Search
Semantic search converts the user's query into an embedding using:
sentence-transformers/all-MiniLM-L6-v2
The embedding is then searched against the Elasticsearch vector index.
Example:
device for connecting computers without cables
This allows searches based on meaning rather than only exact keywords.
Standalone semantic search is available through:
semantic_search.py

8. Hybrid Search
Hybrid search combines:
BM25 search
Semantic/vector search
The project uses Reciprocal Rank Fusion (RRF).
The RRF configuration uses:
RRF_K = 60
The ranking contribution is calculated from the result rank rather than directly comparing BM25 and semantic scores.
The hybrid retriever combines both result lists and returns the highest-ranked products.

9. Query Rewriting
The system supports follow-up questions.
For example:

User:
What is the price of the CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT?

Assistant:
The price is $8409.19.

User:
Who manufactures it?

The query rewriting component uses conversation history to turn the follow-up question into a standalone search query.
Example rewritten query:
CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT manufacturer
This rewritten query is then used for product retrieval.

10. RAG
The RAG pipeline consists of:

User Question
      |
      v
Query Rewriting
      |
      v
Product Retrieval
      |
      v
Build Product Context
      |
      v
LLM
      |
      v
Answer

The LLM is instructed to answer using the retrieved product context.
If the required information cannot be found in the product context, the system responds:
I don't have enough information in the product data.

11. LLM
The project uses OpenRouter through the OpenAI-compatible client.
The configured model is:
openai/gpt-4o-mini
The API key is loaded from:
.env
The .env file should never be committed to source control.

12. FastAPI Search API
The BM25 search API is implemented in:
api.py
Run it with:
</> Bash
uvicorn api:app --host 127.0.0.1 --port 8000
Endpoints
Health check:
GET /
Elasticsearch mapping:
GET /mapping
BM25 search:
GET /search?q=wireless%20networking&size=5

13. FastAPI RAG API
The RAG API is implemented in:
rag_api.py
Run it with:
</> Bash
uvicorn rag_api:app --host 127.0.0.1 --port 8001
Endpoints
BM25 RAG:
POST /rag
Semantic RAG:
POST /rag/semantic
Hybrid RAG:
POST /rag/hybrid

The RAG request supports:

question
result size
conversation history

14. Conversation History
Conversation history is represented using:
</> JSON
{
  "user": "question",
  "assistant": "answer"
}

History is used to resolve follow-up references such as:

it
that product
this product
its
who manufactures it
what category is it
what is its price

15. Command-Line Chatbot
The command-line chatbot is implemented in:
chatbot.py
Run:
</> Bash
python chatbot.py
The chatbot communicates with:
http://127.0.0.1:8001/rag/hybrid
Type:
exit
to stop the chatbot.

16. Embedding Generation
Semantic embeddings are generated by:
generate_embeddings.py

The script:

Reads products from PostgreSQL.
Builds product text.
Generates embeddings.
Uses all-MiniLM-L6-v2.
Indexes the embeddings into the semantic Elasticsearch index.

17. Product Import
PostgreSQL import:
scripts/import_products_to_postgres.py
Elasticsearch import:
scripts/import_products_to_elasticsearch.py
The project contains 500 products in PostgreSQL and Elasticsearch.

18. Validation
The project contains automated validation tests.
RAG validation
</> Bash
python -m rag.test_rag_validation
Result:
ALL RAG VALIDATION TESTS PASSED

Tests include:

Exact product lookup
BM25 retrieval
Semantic retrieval
Hybrid RRF retrieval
Price questions
Manufacturer questions
Category questions
Nonexistent product handling
RAG answer generation
Follow-up manufacturer questions
Follow-up category questions
Follow-up price questions

Search API validation
</> Bash
python test_search_api.py
Result:
ALL SEARCH API TESTS PASSED

Tests include:

GET /mapping
GET /search BM25
Exact product search
Search size parameter

RAG API validation
</> Bash
python test_rag_api.py
Result:
ALL RAG API TESTS PASSED

Tests include:

POST /rag
POST /rag/semantic
POST /rag/hybrid
Hybrid follow-up manufacturer
Hybrid follow-up category
Hybrid follow-up price

19. Project Structure

product-rag/
|
├── api.py
├── app_search.py
├── chatbot.py
├── generate_embeddings.py
├── rag_api.py
├── semantic_search.py
├── test_rag_api.py
├── test_search_api.py
├── README.md
|
├── data/
│   └── products_500_backup.txt
|
├── rag/
│   ├── __init__.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── retriever.py
│   ├── test_rag_pipeline.py
│   ├── test_rag_validation.py
│   └── test_retriever.py
|
└── scripts/
    ├── import_products_to_elasticsearch.py
    └── import_products_to_postgres.py
    
20. Environment
The project uses a Python virtual environment:
.venv/
Environment variables are stored locally in:
.env
The .env file is excluded through .gitignore.

21. Important Elasticsearch Port
Chatbot #2 uses:
localhost:9201
The project must not use the Elasticsearch instance belonging to Chatbot #1.

22. Current Status
The current implementation has been validated successfully.

500 products                       PASS
PostgreSQL import                  PASS
Elasticsearch import               PASS
BM25 search                        PASS
Semantic search                    PASS
Hybrid RRF search                  PASS
RAG retrieval                      PASS
LLM answer generation              PASS
Query rewriting                    PASS
Conversation history               PASS
Search API                         PASS
RAG API                            PASS
CLI chatbot                        PASS
Automated validation               PASS

The project is currently ready for final review and demonstration.
