"""
End-to-end RAG query: retrieve chunks -> Groq generation with strict grounding.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from embed_and_retrieve import RetrievedChunk, retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
REFUSAL_PHRASE = "I don't have enough information on that."

SYSTEM_PROMPT = f"""You are a grounded Q&A assistant for an unofficial Fast & Furious knowledge base.

Rules you MUST follow:
1. Answer ONLY using information explicitly stated in the provided documents.
2. Do NOT use outside knowledge, training data, or assumptions.
3. If the documents do not contain enough information to answer the question, respond with exactly: "{REFUSAL_PHRASE}"
4. Do not invent cast, dates, plot details, box office figures, or opinions not in the documents.
5. Do not cite or name source files in your answer — sources are shown separately to the user."""


def format_context(chunks: list[RetrievedChunk]) -> str:
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        meta = chunk.metadata
        label = (
            f"[Document {i} | {meta['source_file']} | {meta['movie']} | {meta['section']}]"
        )
        parts.append(f"{label}\n{chunk.text}")
    return "\n\n".join(parts)


def format_sources(chunks: list[RetrievedChunk]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        meta = chunk.metadata
        line = f"{meta['source_file']} — {meta['movie']} / {meta['section']}"
        if line not in seen:
            seen.add(line)
            sources.append(line)
    return sorted(sources)


def ask(question: str) -> dict[str, str | list[str]]:
    """Retrieve context, generate a grounded answer, return answer + programmatic sources."""
    chunks = retrieve(question)
    context = format_context(chunks)
    sources = format_sources(chunks)

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Documents:\n{context}\n\n"
                    f"Question: {question}\n\n"
                    "Answer using only the documents above."
                ),
            },
        ],
    )

    answer = response.choices[0].message.content or REFUSAL_PHRASE
    return {"answer": answer.strip(), "sources": sources}


if __name__ == "__main__":
    tests = [
        "Which movie introduced Luke Hobbs, and who plays him?",
        "Which film changed the franchise from street racing into a heist/action series?",
        "Who directed The Dark Knight?",
    ]
    for q in tests:
        result = ask(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer']}")
        print("Sources:")
        for s in result["sources"]:
            print(f"  • {s}")
