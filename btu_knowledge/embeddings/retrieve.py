"""
04_retrieve.py
Given a student question, retrieves the most relevant chunks from ChromaDB.
This is the retrieval step used by apps/knowledge.py at query time.

Can also be run standalone to test retrieval:
  python btu_knowledge/embeddings/04_retrieve.py
"""

import os
import time
from pathlib import Path

import voyageai
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────

CHROMA_PATH     = Path("btu_knowledge/vectorstore")
COLLECTION_NAME = "btu_faq"
VOYAGE_MODEL    = "voyage-3"
TOP_K           = 4          # number of chunks to retrieve per query

# ── Core retrieval function (used by apps/knowledge.py) ──────────────────────

def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        raise EnvironmentError("VOYAGE_API_KEY not set.")

    vo         = voyageai.Client(api_key=api_key)
    client     = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_collection(COLLECTION_NAME)

    # input_type="query" is important — different from "document"
    result      = vo.embed([query], model=VOYAGE_MODEL, input_type="query")
    query_embed = result.embeddings[0]

    results = collection.query(
        query_embeddings=[query_embed],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text":       doc,
            "section":    meta.get("section", ""),
            "question":   meta.get("question", ""),
            "source_url": meta.get("source_url", ""),
            "score":      round(1 - dist, 4),
        })

    return hits


# ── Standalone test ───────────────────────────────────────────────────────────

def main():
    test_queries = [
        "What documents do I need to apply?",
        "How many times can I fail an exam?",
        "What is the internship requirement?",
        "I missed an exam because I was sick, what do I do?",
    ]

    for i, query in enumerate(test_queries):
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        hits = retrieve(query, top_k=2)
        for j, hit in enumerate(hits, 1):
            print(f"\n  [{j}] Score: {hit['score']} | {hit['section']}")
            print(f"      Q: {hit['question'][:70]}")
            print(f"      A: {hit['text'][hit['text'].find('A:')+2:].strip()[:120]}...")

        # Respect Voyage AI free tier: 3 requests/minute
        if i < len(test_queries) - 1:
            print("\n  (waiting 20s for Voyage AI rate limit...)")
            time.sleep(20)


if __name__ == "__main__":
    main()