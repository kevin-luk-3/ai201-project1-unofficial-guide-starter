"""
Embed chunked corpus with all-MiniLM-L6-v2 and store in ChromaDB.

Build-time: chunk_all_documents() -> encode -> collection.add()
Query-time: encode question -> collection.query() -> top-k RetrievedChunk results
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from chunk_documents import Chunk, chunk_all_documents

MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "fast_furious_chunks"
BATCH_SIZE = 64

_embedder: SentenceTransformer | None = None


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    distance: float


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(MODEL_NAME)
    return _embedder


def chunk_id(chunk: Chunk) -> str:
    return f"{chunk.source_file}|{chunk.movie}|{chunk.section}|{chunk.sub_chunk}"


def get_collection(persist_dir: Path = CHROMA_DIR):
    client = chromadb.PersistentClient(path=str(persist_dir))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_index(persist_dir: Path = CHROMA_DIR, force_rebuild: bool = False) -> int:
    """Chunk corpus, embed with MiniLM, and store vectors + metadata in ChromaDB."""
    chunks = chunk_all_documents()
    if not chunks:
        return 0

    collection = get_collection(persist_dir)

    if not force_rebuild and collection.count() == len(chunks):
        return len(chunks)

    if force_rebuild or collection.count() > 0:
        client = chromadb.PersistentClient(path=str(persist_dir))
        client.delete_collection(COLLECTION_NAME)
        collection = get_collection(persist_dir)

    model = get_embedder()
    texts = [c.text for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=BATCH_SIZE)
    embeddings = embeddings.tolist()

    ids = [chunk_id(c) for c in chunks]
    metadatas = [c.to_metadata() for c in chunks]

    for start in range(0, len(chunks), BATCH_SIZE):
        end = start + BATCH_SIZE
        collection.add(
            ids=ids[start:end],
            documents=texts[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    return len(chunks)


def retrieve(query: str, k: int = TOP_K, persist_dir: Path = CHROMA_DIR) -> list[RetrievedChunk]:
    """Embed query and return top-k nearest chunks from ChromaDB."""
    model = get_embedder()
    collection = get_collection(persist_dir)

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved: list[RetrievedChunk] = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for text, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(RetrievedChunk(text=text, metadata=metadata, distance=distance))

    return retrieved


def print_retrieval_results(query: str, results: list[RetrievedChunk]) -> None:
    print(f"\nQuery: {query}")
    for i, hit in enumerate(results, start=1):
        meta = hit.metadata
        print(
            f"  {i}. [{meta['source_file']}] {meta['movie']} / {meta['section']} "
            f"({meta['sub_chunk']}/{meta['sub_chunk_total']}) — distance: {hit.distance:.4f}"
        )
        for line in hit.text.splitlines():
            print(f"     {line}")
        print()


EVAL_QUESTIONS = [
    "Who plays Dom?",
    "What year did the first movie come out?",
    "What happens in movie 3?",
]


if __name__ == "__main__":
    count = build_index(force_rebuild=True)
    print(f"Indexed {count} chunks in {CHROMA_DIR}")

    for question in EVAL_QUESTIONS:
        hits = retrieve(question)
        print_retrieval_results(question, hits)
