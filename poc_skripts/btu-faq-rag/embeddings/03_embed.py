"""
03_embed.py
Embeds chunks using OpenAI and stores them in ChromaDB.
Run this once (or re-run whenever faq_general.json is updated).
Usage: python btu_knowledge/scraper/03_embed.py
"""
import json
import os
from pathlib import Path
import time
from openai import OpenAI
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────
CHUNKS_PATH      = Path("data/chunks.json")
CHROMA_PATH      = Path("data/vectorstore")
COLLECTION_NAME  = "btu_faq"
OPENAI_MODEL     = "text-embedding-3-small"  # or "text-embedding-3-large"
BATCH_SIZE       = 100                        # OpenAI supports up to 2048 inputs per request

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Load chunks
    if not CHUNKS_PATH.exists():
        print(f"Chunks file not found: {CHUNKS_PATH}")
        print("Run 02_chunk.py first.")
        return

    with open(CHUNKS_PATH, encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    # Init OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Run: export OPENAI_API_KEY='your_key_here'")
        return

    client_openai = OpenAI(api_key=api_key)

    # Init ChromaDB (persistent local storage)
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client     = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}   # cosine similarity
    )

    # Embed in batches and upsert into ChromaDB
    texts     = [c["text"]     for c in chunks]
    ids       = [c["chunk_id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    all_embeddings = []
    total_batches  = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(texts), BATCH_SIZE):
        batch     = texts[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        response = client_openai.embeddings.create(
            input=batch,
            model=OPENAI_MODEL,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

        # Small pause to avoid hitting rate limits on large datasets
        if i + BATCH_SIZE < len(texts):
            time.sleep(0.5)

    # Upsert into ChromaDB
    collection.upsert(
        ids        = ids,
        documents  = texts,
        embeddings = all_embeddings,
        metadatas  = metadatas,
    )

    print(f"\n✅ Done! {len(chunks)} chunks embedded and stored in {CHROMA_PATH}")
    print(f"   Collection: '{COLLECTION_NAME}' | Model: {OPENAI_MODEL} | Total items: {collection.count()}")

if __name__ == "__main__":
    main()