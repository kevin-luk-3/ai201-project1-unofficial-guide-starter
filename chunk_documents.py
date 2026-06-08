"""
Ingest and chunk Fast & Furious corpus files per planning.md.

Two-stage chunking:
  1. Split on === MOVIE: and ## delimiters (with movie metadata).
  2. Sub-split sections > 500 chars on paragraph boundaries with 1-paragraph overlap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"
MAX_BODY_CHARS = 400  # body only; metadata header adds ~80–120 chars on top
OVERLAP_PARAGRAPHS = 1

MOVIE_BLOCK_RE = re.compile(r"(?m)^=== MOVIE:\s*(.+?)\s*===\s*$")
SECTION_RE = re.compile(r"(?m)^## (.+)$")


@dataclass
class Chunk:
    text: str
    movie: str
    year: str
    source: str
    source_url: str
    source_file: str
    section: str
    sub_chunk: int
    sub_chunk_total: int
    char_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.char_count = len(self.text)

    def to_metadata(self) -> dict:
        return {
            "movie": self.movie,
            "year": self.year,
            "source": self.source,
            "source_url": self.source_url,
            "source_file": self.source_file,
            "section": self.section,
            "sub_chunk": self.sub_chunk,
            "sub_chunk_total": self.sub_chunk_total,
            "char_count": self.char_count,
        }


def load_document(path: Path) -> str:
    """Load a corpus file and strip the file-level CORPUS header."""
    raw = path.read_text(encoding="utf-8")
    marker = "=== MOVIE:"
    if marker in raw:
        return raw[raw.index(marker) :]
    return raw.strip()


def parse_key_value(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    key, _, value = line.partition(":")
    return key.strip(), value.strip()


def split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    """Fallback when a single paragraph exceeds max_chars."""
    if len(paragraph) <= max_chars:
        return [paragraph]

    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    if len(sentences) <= 1:
        parts: list[str] = []
        start = 0
        while start < len(paragraph):
            parts.append(paragraph[start : start + max_chars])
            start += max_chars
        return parts

    pieces: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        addition = len(sentence) + (1 if current else 0)
        if current and current_len + addition > max_chars:
            pieces.append(" ".join(current))
            current = [sentence]
            current_len = len(sentence)
        else:
            current.append(sentence)
            current_len += addition
    if current:
        pieces.append(" ".join(current))
    return pieces


def subsplit_section(
    text: str,
    max_chars: int = MAX_BODY_CHARS,
    overlap_paragraphs: int = OVERLAP_PARAGRAPHS,
) -> list[str]:
    """Split oversized sections on paragraph boundaries with optional overlap."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    paragraphs: list[str] = []
    for para in re.split(r"\n\n+", text):
        para = para.strip()
        if not para:
            continue
        paragraphs.extend(split_long_paragraph(para, max_chars))

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        addition = len(para) + (2 if current else 0)
        if current and current_len + addition > max_chars:
            chunks.append("\n\n".join(current))
            overlap = current[-overlap_paragraphs:] if overlap_paragraphs else []
            current = overlap + [para]
            current_len = sum(len(p) for p in current) + 2 * max(0, len(current) - 1)
        else:
            current.append(para)
            current_len += addition

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def format_chunk_text(
    movie: str,
    year: str,
    source: str,
    section: str,
    sub_chunk: int,
    sub_chunk_total: int,
    body: str,
) -> str:
    """Prefix chunk body with metadata so embeddings retain movie/section context."""
    section_label = section if sub_chunk_total == 1 else f"{section} ({sub_chunk}/{sub_chunk_total})"
    header = f"MOVIE: {movie} | YEAR: {year} | SOURCE: {source} | SECTION: {section_label}"
    return f"{header}\n\n{body.strip()}"


def chunk_movie_block(block: str, source_file: str) -> list[Chunk]:
    """Parse one === MOVIE: block into Chunk objects."""
    lines = block.strip().splitlines()
    if not lines:
        return []

    movie = lines[0].strip()
    metadata: dict[str, str] = {"movie": movie}
    content_start = 1

    for i in range(1, len(lines)):
        line = lines[i]
        if line.startswith("##"):
            content_start = i
            break
        parsed = parse_key_value(line)
        if parsed and parsed[0] in {"YEAR", "SOURCE", "SOURCE_URL"}:
            metadata[parsed[0].lower()] = parsed[1]

    year = metadata.get("year", "")
    source = metadata.get("source", "")
    source_url = metadata.get("source_url", "")

    remaining = "\n".join(lines[content_start:])
    section_splits = SECTION_RE.split(remaining)
    if len(section_splits) < 2:
        return []

    chunks: list[Chunk] = []
    # split() with capturing group: [preamble, section1, body1, section2, body2, ...]
    pairs = zip(section_splits[1::2], section_splits[2::2])
    for section_name, section_body in pairs:
        section_name = section_name.strip()
        section_body = re.sub(r"\n---\s*$", "", section_body.strip())
        if not section_body:
            continue

        sub_chunks = subsplit_section(section_body)
        total = len(sub_chunks)
        for idx, body in enumerate(sub_chunks, start=1):
            chunks.append(
                Chunk(
                    text=format_chunk_text(movie, year, source, section_name, idx, total, body),
                    movie=movie,
                    year=year,
                    source=source,
                    source_url=source_url,
                    source_file=source_file,
                    section=section_name,
                    sub_chunk=idx,
                    sub_chunk_total=total,
                )
            )

    return chunks


def chunk_file(path: Path) -> list[Chunk]:
    """Load and chunk a single corpus file."""
    text = load_document(path)
    blocks = MOVIE_BLOCK_RE.split(text)
    # split with capturing group: [preamble, movie1, block1, movie2, block2, ...]
    chunks: list[Chunk] = []
    for i in range(1, len(blocks), 2):
        if i + 1 >= len(blocks):
            break
        movie_name = blocks[i].strip()
        block_body = blocks[i + 1]
        block = f"{movie_name}\n{block_body}"
        chunks.extend(chunk_movie_block(block, path.name))
    return chunks


def chunk_all_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[Chunk]:
    """Load and chunk every .txt file in documents/."""
    all_chunks: list[Chunk] = []
    for path in sorted(documents_dir.glob("*.txt")):
        all_chunks.extend(chunk_file(path))
    return all_chunks


def print_sample(chunks: list[Chunk], n: int = 5) -> None:
    print(f"\n--- Sample chunks (first {n}) ---\n")
    for chunk in chunks[:n]:
        print(f"[{chunk.source_file}] {chunk.movie} / {chunk.section} ({chunk.sub_chunk}/{chunk.sub_chunk_total})")
        print(f"  chars: {chunk.char_count}")
        print(chunk.text)
        print()


def print_stats(chunks: list[Chunk]) -> None:
    if not chunks:
        print("No chunks produced — check document format.")
        return
    counts = [c.char_count for c in chunks]
    over_500 = sum(1 for c in counts if c > 500)
    subsplit_count = sum(1 for c in chunks if c.sub_chunk_total > 1)
    by_file: dict[str, int] = {}
    for c in chunks:
        by_file[c.source_file] = by_file.get(c.source_file, 0) + 1

    print("--- Chunking stats ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Min chars: {min(counts)} | Max chars: {max(counts)} | Avg chars: {sum(counts) / len(counts):.0f}")
    print(f"Chunks > 500 chars: {over_500}")
    print(f"Sections that were sub-split: {subsplit_count}")
    print("Per file:")
    for name, count in sorted(by_file.items()):
        print(f"  {name}: {count}")


if __name__ == "__main__":
    chunks = chunk_all_documents()
    print_stats(chunks)
    print_sample(chunks, n=100)
