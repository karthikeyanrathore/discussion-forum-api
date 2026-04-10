"""
04_retrieve.py
Given a student question, retrieves the most relevant chunks from ChromaDB.
This is the retrieval step used by apps/knowledge.py at query time.
Can also be run standalone to test retrieval:
  python btu_knowledge/embeddings/04_retrieve.py
"""
import os
from pathlib import Path
from openai import OpenAI
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_PATH     = Path("data/vectorstore")
COLLECTION_NAME = "btu_faq"
OPENAI_MODEL    = "text-embedding-3-small"
TOP_K           = 4          # number of chunks to retrieve per query

# ── Core retrieval function (used by apps/knowledge.py) ──────────────────────
def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set.")

    client_openai = OpenAI(api_key=api_key)
    client        = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection    = client.get_collection(COLLECTION_NAME)

    response    = client_openai.embeddings.create(input=[query], model=OPENAI_MODEL)
    query_embed = response.data[0].embedding

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

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        hits = retrieve(query, top_k=2)
        for j, hit in enumerate(hits, 1):
            print(f"\n  [{j}] Score: {hit['score']} | {hit['section']}")
            print(f"      Q: {hit['question'][:70]}")
            print(f"      A: {hit['text'][hit['text'].find('A:')+2:].strip()[:120]}...")

if __name__ == "__main__":
    main()