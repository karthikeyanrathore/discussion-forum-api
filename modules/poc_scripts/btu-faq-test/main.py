#!/usr/bin/env python3
"""
ask_bot.py
Simple CLI for the BTU RAG pipeline.
Uses Anthropic Claude as primary LLM, falls back to OpenAI if key is missing.
Usage:
    python ask_bot.py
    python ask_bot.py "How many times can I fail an exam?"
"""

import os
import sys
from embeddings.retrieve import retrieve

# ── Config ────────────────────────────────────────────────────────────────────
ANTHROPIC_MODEL = "claude-sonnet-4-6"
OPENAI_MODEL    = "gpt-4o"
MAX_TOKENS      = 1024
TOP_K           = 4

SYSTEM_PROMPT = """You are a helpful assistant for students in the Artificial Intelligence Master's programme at BTU Cottbus-Senftenberg.
You answer student questions using ONLY the official BTU information provided to you in the context below.
Rules:
- Answer clearly and concisely based only on the provided context.
- If the context does not contain enough information to answer, say: "I don't have enough information to answer this. Please contact the BTU examination office directly."
- Do not make up information.
- If relevant, mention where the student can find more details (source URLs from the context).
- Keep your tone friendly and helpful."""


# ── LLM call (Anthropic → OpenAI fallback) ───────────────────────────────────
def call_llm(user_message: str) -> tuple[str, str]:
    """
    Returns (answer_text, provider_used).
    Tries Anthropic first; falls back to OpenAI if ANTHROPIC_API_KEY is absent.
    Raises EnvironmentError if neither key is set.
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key    = os.environ.get("OPENAI_API_KEY")

    if anthropic_key:
        from anthropic import Anthropic
        client   = Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model      = ANTHROPIC_MODEL,
            max_tokens = MAX_TOKENS,
            system     = SYSTEM_PROMPT,
            messages   = [{"role": "user", "content": user_message}],
        )
        return response.content[0].text, "Anthropic"

    if openai_key:
        from openai import OpenAI
        client   = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model      = OPENAI_MODEL,
            max_tokens = MAX_TOKENS,
            messages   = [
                {"role": "system",  "content": SYSTEM_PROMPT},
                {"role": "user",    "content": user_message},
            ],
        )
        return response.choices[0].message.content, "OpenAI"

    raise EnvironmentError(
        "No LLM API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY."
    )


# ── Core function ─────────────────────────────────────────────────────────────
def answer_question(question: str) -> dict:
    chunks = retrieve(question, top_k=TOP_K)
    if not chunks:
        return {
            "answer":   "I could not find relevant information in the BTU knowledge base. Please contact the examination office directly.",
            "sources":  [],
            "chunks_used": 0,
            "provider": "none",
        }

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i} — {chunk['section']}]\n"
            f"{chunk['text']}\n"
            f"URL: {chunk['source_url']}"
        )

    user_message = (
        f"Context from BTU official sources:\n\n"
        f"{'\n\n---\n\n'.join(context_parts)}\n\n"
        f"---\n\n"
        f"Student question: {question}"
    )

    answer, provider = call_llm(user_message)

    return {
        "answer":   answer,
        "sources":  [
            {
                "section":    c["section"],
                "question":   c["question"],
                "source_url": c["source_url"],
                "score":      c["score"],
            }
            for c in chunks
        ],
        "chunks_used": len(chunks),
        "provider":    provider,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
def print_result(question: str, result: dict):
    print(f"\n{'='*60}")
    print(f"Q: {question}")
    print(f"{'='*60}")
    print(f"\n{result['answer']}\n")
    if result["sources"]:
        print(f"── Sources ({result['chunks_used']} chunks used) ──")
        for i, src in enumerate(result["sources"], 1):
            print(f"  {i}. [{src['section']}] {src['source_url']}  (score: {src['score']:.3f})")
    print(f"\n  Provider: {result['provider']}\n")


def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        result = answer_question(question)
        print_result(question, result)
        return

    print("BTU AskBot — type 'exit' or Ctrl+C to quit.\n")
    while True:
        try:
            question = input("Your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Bye!")
            break

        result = answer_question(question)
        print_result(question, result)


if __name__ == "__main__":
    main()