"""
03_embed.py
Embeds chunks using Voyage AI and stores them in ChromaDB.
Run this once (or re-run whenever faq_general.json is updated).

Usage: python btu_knowledge/scraper/03_embed.py
"""

import json
import os
from pathlib import Path

import voyageai
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────

CHUNKS_PATH      = Path("btu_knowledge/data/chunks.json")
CHROMA_PATH      = Path("btu_knowledge/vectorstore")
COLLECTION_NAME  = "btu_faq"
VOYAGE_MODEL     = "voyage-3"          # Voyage AI embedding model
BATCH_SIZE       = 64                  # Voyage AI max batch size

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

    # Init Voyage AI
    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        print("ERROR: VOYAGE_API_KEY environment variable not set.")
        print("Run: export VOYAGE_API_KEY='your_key_here'")
        return
    vo = voyageai.Client(api_key=api_key)

    # Init ChromaDB (persistent local storage)
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client     = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}   # cosine similarity
    )

    # Embed in batches and upsert into ChromaDB
    texts      = [c["text"]     for c in chunks]
    ids        = [c["chunk_id"] for c in chunks]
    metadatas  = [c["metadata"] for c in chunks]

    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        print(f"  Embedding batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)...")
        result = vo.embed(batch, model=VOYAGE_MODEL, input_type="document")
        all_embeddings.extend(result.embeddings)

    # Upsert into ChromaDB
    collection.upsert(
        ids        = ids,
        documents  = texts,
        embeddings = all_embeddings,
        metadatas  = metadatas,
    )

    print(f"\n✅ Done! {len(chunks)} chunks embedded and stored in {CHROMA_PATH}")
    print(f"   Collection: '{COLLECTION_NAME}' | Total items: {collection.count()}")


if __name__ == "__main__":
    main()