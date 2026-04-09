"""
apps/knowledge.py
RAG pipeline: retrieves relevant BTU FAQ chunks and generates
an answer using Claude.

Usage (from resources.py):
    from apps.knowledge import answer_question
    response = answer_question("How many times can I fail an exam?")
"""

import os
from anthropic import Anthropic
from btu_knowledge.embeddings.retrieve import retrieve

# ── Config ────────────────────────────────────────────────────────────────────

ANTHROPIC_MODEL = "claude-sonnet-4-6"
MAX_TOKENS      = 1024
TOP_K           = 4       # number of chunks to retrieve

SYSTEM_PROMPT = """You are a helpful assistant for students in the Artificial Intelligence Master's programme at BTU Cottbus-Senftenberg.

You answer student questions using ONLY the official BTU information provided to you in the context below.

Rules:
- Answer clearly and concisely based only on the provided context.
- If the context does not contain enough information to answer, say: "I don't have enough information to answer this. Please contact the BTU examination office directly."
- Do not make up information.
- If relevant, mention where the student can find more details (source URLs from the context).
- Keep your tone friendly and helpful."""

# ── Core function ─────────────────────────────────────────────────────────────

def answer_question(question: str) -> dict:
    """
    Given a student question:
      1. Retrieve top-k relevant chunks from ChromaDB
      2. Format them as context
      3. Ask Claude to answer using that context

    Returns:
      {
        "answer": str,
        "sources": [{"section": str, "question": str, "source_url": str}],
        "chunks_used": int
      }
    """
    # Step 1 — retrieve relevant chunks
    chunks = retrieve(question, top_k=TOP_K)

    if not chunks:
        return {
            "answer": "I could not find relevant information in the BTU knowledge base. Please contact the examination office directly.",
            "sources": [],
            "chunks_used": 0,
        }

    # Step 2 — format context for Claude
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i} — {chunk['section']}]\n"
            f"{chunk['text']}\n"
            f"URL: {chunk['source_url']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    user_message = (
        f"Context from BTU official sources:\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"Student question: {question}"
    )

    # Step 3 — ask Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set.")

    client   = Anthropic(api_key=api_key)
    response = client.messages.create(
        model      = ANTHROPIC_MODEL,
        max_tokens = MAX_TOKENS,
        system     = SYSTEM_PROMPT,
        messages   = [{"role": "user", "content": user_message}],
    )

    answer = response.content[0].text

    # Step 4 — collect sources for citation
    sources = [
        {
            "section":    chunk["section"],
            "question":   chunk["question"],
            "source_url": chunk["source_url"],
            "score":      chunk["score"],
        }
        for chunk in chunks
    ]

    return {
        "answer":      answer,
        "sources":     sources,
        "chunks_used": len(chunks),
    }