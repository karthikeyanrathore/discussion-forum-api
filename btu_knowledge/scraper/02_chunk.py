"""
02_chunk.py
Splits faq_general.json into RAG-ready chunks.
Saves to btu_knowledge/data/chunks.json

Improvements over v1:
  1. Long linked_content is split into sub-chunks (max ~400 tokens)
     instead of one giant chunk — keeps embeddings precise
  2. Each chunk tracks chunk_type (faq_direct vs faq_linked)
     and linked_source_url separately for better citation
  3. Q is prepended to every sub-chunk so context is never lost
"""

import json
import re
from pathlib import Path

INPUT_PATH  = Path("btu_knowledge/data/faq_general.json")
OUTPUT_PATH = Path("btu_knowledge/data/chunks.json")

# 400 tokens * 4 chars/token = 1600 chars max per chunk
MAX_CHUNK_CHARS = 1600


def estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 characters."""
    return len(text) // 4


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def split_long_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """
    Split long text into chunks using paragraph → sentence boundaries.
    Never cuts mid-sentence. Based on recursive character splitting strategy.
    """
    if len(text) <= max_chars:
        return [text]

    chunks  = []
    current = ""

    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}".strip()

        elif len(para) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for sentence in split_into_sentences(para):
                if len(current) + len(sentence) + 1 <= max_chars:
                    current = f"{current} {sentence}".strip()
                else:
                    if current:
                        chunks.append(current)
                    current = sentence
        else:
            if current:
                chunks.append(current)
            current = para

    if current:
        chunks.append(current)

    return chunks if chunks else [text[:max_chars]]


def make_chunks(faq_data: list[dict]) -> list[dict]:
    chunks    = []
    chunk_idx = 0

    for entry in faq_data:
        question       = entry["question"]
        answer         = entry["answer"]
        linked_content = entry["linked_content"]
        section        = entry["section"]
        source_url     = entry["source_url"]
        linked_urls    = entry.get("linked_urls", [])

        linked_source_url = next(
            (u for u in linked_urls if "b-tu.de" in u), ""
        )

        # Chunk A: Direct FAQ answer
        if answer:
            direct_text = f"Q: {question}\nA: {answer}"
            chunks.append({
                "chunk_id": f"faq_{chunk_idx:03d}",
                "text":     direct_text,
                "metadata": {
                    "section":           section,
                    "question":          question,
                    "source_url":        source_url,
                    "chunk_type":        "faq_direct",
                    "linked_source_url": linked_source_url,
                    "tokens_approx":     estimate_tokens(direct_text),
                }
            })
            print(f"  ✓ faq_{chunk_idx:03d} [direct]  | {section[:25]} | {question[:45]}...")
            chunk_idx += 1

        # Chunk B: Linked page content — split if long
        if linked_content:
            sub_texts = split_long_text(linked_content, MAX_CHUNK_CHARS)
            for j, sub_text in enumerate(sub_texts):
                full_text = f"Q: {question}\nA: {sub_text}"
                chunks.append({
                    "chunk_id": f"faq_{chunk_idx:03d}",
                    "text":     full_text,
                    "metadata": {
                        "section":           section,
                        "question":          question,
                        "source_url":        linked_source_url or source_url,
                        "chunk_type":        "faq_linked",
                        "linked_source_url": linked_source_url,
                        "sub_chunk":         j + 1,
                        "total_sub_chunks":  len(sub_texts),
                        "tokens_approx":     estimate_tokens(full_text),
                    }
                })
                print(
                    f"  ✓ faq_{chunk_idx:03d} [linked {j+1}/{len(sub_texts)}] "
                    f"| {section[:20]} | {question[:30]}... "
                    f"(~{estimate_tokens(full_text)} tokens)"
                )
                chunk_idx += 1

        if not answer and not linked_content:
            print(f"  ⚠ Skipping (no content): {question[:60]}")

    return chunks


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

    direct = [c for c in chunks if c["metadata"]["chunk_type"] == "faq_direct"]
    linked = [c for c in chunks if c["metadata"]["chunk_type"] == "faq_linked"]
    avg_t  = sum(c["metadata"]["tokens_approx"] for c in chunks) // len(chunks)

    print(f"\n✅ Done! {len(chunks)} total chunks saved to {OUTPUT_PATH}")
    print(f"   Direct FAQ chunks : {len(direct)}")
    print(f"   Linked page chunks: {len(linked)}")
    print(f"   Avg tokens/chunk  : ~{avg_t}")


if __name__ == "__main__":
    main()