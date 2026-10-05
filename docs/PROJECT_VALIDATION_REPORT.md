# Product RAG Project — Validation Report

## 1. Project Overview

This project implements a product-search chatbot using a 500-product dataset.

The system provides:

- PostgreSQL product storage
- Elasticsearch BM25 search
- Elasticsearch semantic/vector search
- Hybrid retrieval
- RAG pipeline
- Query rewriting for follow-up questions
- FastAPI endpoints
- Next.js chatbot interface
- Automated validation tests

---

## 2. Dataset

Source file:

`products_500_backup.txt`

Dataset size:

**500 product records**

The source file is an Elasticsearch `_search` response containing 500 product documents.

---

## 3. Database

PostgreSQL database:

`product_rag`

Product table:

`products`

Imported records:

**500 / 500**

The PostgreSQL database provides structured product storage and acts as the source for creating the Elasticsearch indexes.

---

## 4. Elasticsearch

Chatbot #2 uses its own Elasticsearch instance:

```text
http://localhost:9201

BM25 Index
products_vendor_improve_rag
Documents:
500
Purpose:
Lexical/text-based product search using Elasticsearch BM25.

Semantic Index
products_vendor_improve_rag_semantic
Documents:
500
Purpose:
Vector-based semantic product retrieval.
Embedding model:
sentence-transformers/all-MiniLM-L6-v2
Embedding dimensions:
384

5. Elasticsearch Mapping

The BM25 index contains fields including:

Id
Name
Description
ManufacturerName
Category
ListPrice
SearchableText
Specification
Specifications
Quantity
ProductType
Status
StockStatus
Product boolean flags
Product dimensions
Price fields

Important mappings include:

Id                  keyword
Name                text + keyword
Description         text
ManufacturerName    text + keyword
Category            text + keyword
ListPrice           double
Quantity            integer
ProductType         integer
Status              integer

The Specifications object contains fields such as:

Color
Connectivity
Form Factor
Operating System
Ports
Processor
RAM
Resolution
Screen Size
Storage

The following objects have indexing disabled:

Images
VendorInfo
raw_data

The mapping is exposed through:
GET /mapping

6. BM25 Search
BM25 searches the following product fields:

Name
Description
ManufacturerName
Category
SearchableText
Specification

Exact product-name matching is attempted first.
Short queries use stricter matching to reduce irrelevant numeric or partial matches.
Longer queries use more flexible matching.

7. Semantic Search
Semantic search converts the user's question into a 384-dimensional embedding.
The embedding is generated using:
sentence-transformers/all-MiniLM-L6-v2
The vector is searched against:
products_vendor_improve_rag_semantic
The semantic retrieval threshold is:
0.68

8. Hybrid Search
Hybrid search combines:
BM25
+
Semantic Search
The system uses Reciprocal Rank Fusion (RRF):
RRF K = 60
This combines results from both retrieval methods into a single ranked result set.

9. RAG Pipeline
The RAG pipeline follows these steps:

User Question
      ↓
Query Rewriting
      ↓
Product Retrieval
      ↓
BM25 / Semantic / Hybrid
      ↓
Product Context
      ↓
LLM
      ↓
Final Answer

The LLM is instructed to answer using the retrieved product context and conversation history.
If the required information is not available, the system returns:
I don't have enough information in the product data.

10. Query Rewriting

Query rewriting resolves follow-up references such as:

it
that product
this product
its
who makes it
what category is it
what is its price

Example:

Previous question:
What is the price of the CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT?
Follow-up:
Who manufactures it?
Rewritten search query:
CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT manufacturer
This allows the retrieval system to search for the actual product instead of searching only for the word it.

11. Unknown Product Protection
The system includes retrieval thresholds to reduce false-positive results.
Test question:
Tell me about an iPhone 20
Expected behavior:
No products retrieved.
Expected answer:
I don't have enough information in the product data.

This test passed through:

RAG validation
API validation
Browser/frontend validation

12. RAG Automated Validation

The automated RAG validation contains 10 tests:

Exact product retrieval
BM25 retrieval
Semantic retrieval
Hybrid retrieval
Unknown product rejection
RAG price answer
RAG manufacturer answer
RAG unknown product protection
Query rewriting
Follow-up question

Result:
10/10 PASSED

13. FastAPI
The RAG API runs on:
http://127.0.0.1:8001
Endpoints:

GET  /
GET  /mapping

POST /rag
POST /rag/semantic
POST /rag/hybrid

API Validation

The automated API validation contains 6 tests:

API root
Hybrid product question
Semantic API question
BM25 RAG API question
Unknown product protection
Follow-up conversation

Result:
6/6 PASSED

14. Frontend
The frontend is implemented using:

Next.js
React
Tailwind CSS
TypeScript

Frontend URL:
http://localhost:3000
The frontend communicates with:
http://127.0.0.1:8001

The frontend was manually validated for:

Product questions
Product answers
Retrieved product cards
Hybrid search display
Price information
Manufacturer information
Conversation history
Query rewriting
Unknown-product protection
New Chat
Loading state
Input interaction

15. Example Validated Product
Product:
CISCO 5520 WIRELESS CONTROLLER WRACK MOUNTING KIT
Validated manufacturer:
CISCO SYSTEMS
Validated price:
8409.19

16. Validation Summary

| Component                    | Result        |
| ---------------------------- | ------------- |
| Product dataset              | 500 records   |
| PostgreSQL import            | 500/500       |
| BM25 Elasticsearch index     | 500 documents |
| Semantic Elasticsearch index | 500 documents |
| Elasticsearch mapping        | Passed        |
| Mapping API                  | Passed        |
| BM25 retrieval               | Passed        |
| Semantic retrieval           | Passed        |
| Hybrid retrieval             | Passed        |
| RAG validation               | 10/10 passed  |
| API validation               | 6/6 passed    |
| Frontend validation          | Passed        |
| Conversation history         | Passed        |
| Unknown-product protection   | Passed        |

17. Overall Architecture

                              500 Products
                       |
                       v
                  PostgreSQL
                       |
                       v
                 Elasticsearch
                       |
             +---------+---------+
             |                   |
             v                   v
           BM25              Semantic
             |                   |
             +---------+---------+
                       |
                       v
                    Hybrid
                       |
                       v
                  Query/RAG
                       |
             +---------+---------+
             |                   |
             v                   v
       Query Rewriting          LLM
             |                   |
             +---------+---------+
                       |
                       v
                    FastAPI
                       |
                       v
                    Next.js
                       |
                       v
                  Chatbot UI
                  
                  
18. Final Status
The product-search RAG workflow has been implemented and validated across:

Product Data
      ↓
PostgreSQL
      ↓
Elasticsearch
      ↓
BM25
      ↓
Semantic Search
      ↓
Hybrid Retrieval
      ↓
RAG
      ↓
FastAPI
      ↓
Next.js
      ↓
Chatbot

Current automated validation:

RAG: 10/10 PASSED
API: 6/6 PASSED
Frontend: PASSED
Mapping API: PASSED

The project is ready for final demonstration and technical review.



