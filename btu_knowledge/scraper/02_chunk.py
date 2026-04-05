"""
02_chunk.py
Splits faq_general.json into RAG-ready chunks.
Saves to btu_knowledge/data/chunks.json

Each chunk has:
  - chunk_id: unique identifier
  - text: the actual text the LLM will see (question + answer combined)
  - metadata: section, question, source_url for citation
"""

import json
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

INPUT_PATH  = Path("btu_knowledge/data/faq_general.json")
OUTPUT_PATH = Path("btu_knowledge/data/chunks.json")

# ── Chunking ──────────────────────────────────────────────────────────────────

def make_chunks(faq_data: list[dict]) -> list[dict]:
    chunks = []

    for i, entry in enumerate(faq_data):
        question       = entry["question"]
        answer         = entry["answer"]
        linked_content = entry["linked_content"]
        section        = entry["section"]
        source_url     = entry["source_url"]

        # Combine answer + linked content into one full answer text
        full_answer = answer
        if linked_content:
            full_answer = f"{answer} {linked_content}".strip()

        # Skip if truly empty after everything
        if not full_answer:
            print(f"  ⚠ Skipping (no content): {question[:60]}")
            continue

        # Format: "Q: ... A: ..." — this gives the embedding model full context
        text = f"Q: {question}\nA: {full_answer}"

        chunks.append({
            "chunk_id":   f"faq_{i:03d}",
            "text":       text,
            "metadata": {
                "section":    section,
                "question":   question,
                "source_url": source_url,
            }
        })

        print(f"  ✓ chunk faq_{i:03d} | {section[:30]} | {question[:50]}...")

    return chunks


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if not INPUT_PATH.exists():
        print(f"Input file not found: {INPUT_PATH}")
        print("Run 01_scrape.py first.")
        return

    with open(INPUT_PATH, encoding="utf-8") as f:
        faq_data = json.load(f)

    print(f"Loaded {len(faq_data)} FAQ entries from {INPUT_PATH}\n")

    chunks = make_chunks(faq_data)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! {len(chunks)} chunks saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()