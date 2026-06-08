# The Unofficial Guide — Project 1

---

## Domain

This system covers **unofficial Fast & Furious franchise knowledge** — plot and characters, timeline/watch-order confusion, critical and fan reception, box-office performance, production trivia, and how the series evolved from street racing to globe-trotting heist blockbusters.

That knowledge is valuable because Universal's official marketing does not explain *Tokyo Drift*'s timeline placement, which entry introduced Luke Hobbs, why Han is a fan favorite, or where critics and audiences disagree. Real answers live scattered across Wikipedia, fan forums, review aggregators, and editorial retrospectives — no single studio page ties it together.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Wikipedia | Reference (plot, cast, production, timeline) | https://en.wikipedia.org/wiki/Fast_%26_Furious · `documents/wikipedia.txt` |
| 2 | Rotten Tomatoes | Critics (Tomatometer, consensus, audience) | https://www.rottentomatoes.com/m/fast_five · `documents/rotten_tomatoes.txt` |
| 3 | Metacritic | Critics/users (scores, review summaries) | https://www.metacritic.com/movie/fast-five/ · `documents/metacritic.txt` |
| 4 | IMDb | Production trivia, casting notes | https://www.imdb.com/title/tt1596343/ · `documents/imdb.txt` |
| 5 | Box Office Mojo | Financial (worldwide/domestic gross) | https://www.boxofficemojo.com/title/tt2820852/ · `documents/box_office_mojo.txt` |
| 6 | The Numbers | Financial (budget, revenue, profitability) | https://www.the-numbers.com/ · `documents/the_numbers.txt` |
| 7 | Letterboxd | Fan culture (positive/negative reactions) | https://letterboxd.com/film/fast-five/ · `documents/letterboxd.txt` |
| 8 | Reddit | Fan opinions (r/fastandfurious, r/movies threads) | https://www.reddit.com/r/fastandfurious/ · `documents/reddit.txt` |
| 9 | RogerEbert.com | Professional reviews | https://www.rogerebert.com/reviews/fast-five-2011 · `documents/roger_ebert.txt` |
| 10 | Screen Rant | Franchise editorial (timeline, analysis) | https://screenrant.com/fast-five-best-franchise/ · `documents/screen_rant.txt` |

---

## Chunking Strategy

**Chunk size:**

Two-stage chunking in `chunk_documents.py`:

1. **Primary split (delimiter-based):** One chunk per `##` section inside each `=== MOVIE:` block. Each chunk is prefixed with metadata (`MOVIE`, `YEAR`, `SOURCE`, `SECTION`).
2. **Sub-split (size-based):** If a section body exceeds **400 characters** (`MAX_BODY_CHARS`), split on paragraph boundaries (`\n\n`) into smaller pieces targeting ~400–500 characters total including the metadata header. Only Wikipedia `## Plot` sections required sub-splitting.

Most chunks are ~89–400 characters. Sub-split plot chunks average ~300–500 characters (~100–125 tokens), under MiniLM's 256-token limit.

**Overlap:**

0 characters between different `##` sections. **1 paragraph overlap** between sub-chunks within the same section (last paragraph of chunk N repeats as first paragraph of chunk N+1) so plot beats at boundaries are not lost.

**Why these choices fit your documents:**

Delimiter chunking keeps each unit topically coherent — a Hobbs question should retrieve `## Casting Notes`, not an unrelated film's plot. Fixed character windows would split mid-fact (e.g., separating budget from worldwide gross). Wikipedia plots were too long to embed whole; paragraph sub-splitting fixes that without changing the file format. Preprocessing strips the file-level `CORPUS:` header and attaches metadata to every chunk for citations.

**Final chunk count:**

**441 chunks** across all 10 files (min 89 chars, max 840 chars, avg 324 chars).

---

## Embedding Model

**Model used:**

`all-MiniLM-L6-v2` via `sentence-transformers`. Free, runs locally, fast to embed ~441 short chunks, and fits the project's chunk sizes (most under 256 tokens). Cosine similarity in ChromaDB matches normalized MiniLM vectors.

**Production tradeoff reflection:**

With no cost constraint, I would weigh: (1) **context length** — a model supporting longer inputs would reduce need for aggressive plot sub-splitting; (2) **domain accuracy** — a larger model (e.g., `bge-large` or an OpenAI embedding API) may better match casual queries like "most money worldwide" to the right film; (3) **latency** — local MiniLM is fast, but API-hosted models add network cost; (4) **multilingual support** — not useful for this English-only corpus. I would also consider hybrid retrieval (BM25 + vectors) before upgrading the embedding model alone.

---

## Grounded Generation

**System prompt grounding instruction:**

`query.py` sends a strict system prompt to Groq (`llama-3.3-70b-versatile`, `temperature=0`):

```
You are a grounded Q&A assistant for an unofficial Fast & Furious knowledge base.

Rules you MUST follow:
1. Answer ONLY using information explicitly stated in the provided documents.
2. Do NOT use outside knowledge, training data, or assumptions.
3. If the documents do not contain enough information to answer the question, respond with exactly: "I don't have enough information on that."
4. Do not invent cast, dates, plot details, box office figures, or opinions not in the documents.
5. Do not cite or name source files in your answer — sources are shown separately to the user.
```

Retrieved chunks are numbered and labeled (`[Document 1 | wikipedia.txt | Fast Five | Cast]`) in the user message. The model is instructed: "Answer using only the documents above."

**How source attribution is surfaced in the response:**

Sources are **programmatic**, not LLM-generated. After retrieval, `format_sources()` builds a deduplicated list from chunk metadata (e.g., `wikipedia.txt — Fast Five / Cast`) and the Gradio UI displays them in a separate "Retrieved from" panel. This guarantees filenames appear even if the model omits citations.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which movie introduced Luke Hobbs, and who plays him? | *Fast Five* (2011); Dwayne Johnson as Luke Hobbs | Fast Five (2011); Dwayne Johnson. Top chunks: `wikipedia.txt` Franchise Notes, `imdb.txt` Casting Notes/Trivia. | Relevant | Accurate |
| 2 | Why is *Tokyo Drift* placed later in the franchise timeline despite being the third film released? | Release order is 3rd; story chronology places it later (after F6); Han's arc connects to later films | Mentioned release order vs. internal chronology and F6 retcon, but hedged that docs "do not explicitly state why." Retrieved timeline chunks from `wikipedia.txt` and `screen_rant.txt`. | Partially relevant | Partially accurate |
| 3 | Which Fast & Furious film earned the most money worldwide? | *Furious 7* — ~$1.515 billion (`box_office_mojo.txt`, `the_numbers.txt`) | Incorrectly answered *The Fast and the Furious* (2001) at $207.5M. Retrieval returned Revenue sections for films 1 and Tokyo Drift, not Furious 7's franchise-high chunk. | Partially relevant | Inaccurate |
| 4 | Which film changed the franchise from street racing into a heist/action series? | *Fast Five* — Rio heist, vault chase, ensemble template | Fast Five (2011) pivoted from street racing to heist action. Top chunks: `wikipedia.txt` Production, `imdb.txt` Production Facts. | Relevant | Accurate |
| 5 | How did critics and fans react to *F9*? | Polarized: critics mixed (~59% Tomatometer); fans split on space scene, celebrated Han's return | Captured fan negativity on Reddit and audience/critic score gap, but missed Tomatometer ~59% and space-magnet mockery. Retrieved fan/review chunks, not `## Critic Consensus`. | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

Which Fast & Furious film earned the most money worldwide?

**What the system returned:**

The system said *The Fast and the Furious* (2001) earned $207.5 million worldwide — the highest among the retrieved chunks — instead of *Furious 7* at ~$1.515 billion.

**Root cause (tied to a specific pipeline stage):**

**Retrieval (embedding + top-k search).** The correct answer lives in `box_office_mojo.txt` under `## Highest in franchise` ("Furious 7 is the highest-grossing Fast & Furious film worldwide at $1.515 billion"). The query embedding matched generic per-film `## Revenue` sections (similar wording across all 10 films) more strongly than the comparative "highest-grossing" chunk. With top-k=5, Furious 7's franchise summary never reached the LLM context. Generation faithfully summarized what it received — the failure was upstream in retrieval, not hallucination.

**What you would change to fix it:**

Increase top-k to 10; add hybrid keyword search for superlatives ("most", "highest", "worldwide"); or enrich box-office chunks with comparative labels in metadata (e.g., `section: Franchise Rankings`). Query rewriting ("highest grossing film franchise ranking") before embedding would also help.

---

## Spec Reflection

**One way the spec helped you during implementation:**

`planning.md` gave concrete delimiter rules (`=== MOVIE:` / `##`), chunk size targets, overlap policy, and the architecture diagram. That let me prompt AI tools stage-by-stage (chunk → embed → retrieve → generate) with verifiable checkpoints instead of one vague "build a RAG app" request. The 5 eval questions also forced testable questions upfront.

**One way your implementation diverged from the spec, and why:**

Final chunk count was **441** instead of the planned ~380, because Wikipedia plot sub-splits produced more pieces than estimated. I also removed identical `## Common Themes` sections from `letterboxd.txt` during testing — they were duplicate text across all 10 films and polluted retrieval (e.g., crowding out heist/production chunks). That was a corpus cleanup not in the original spec, driven by observed retrieval noise.

---

## AI Usage

**Instance 1 — Chunking pipeline (Milestone 3)**

- *What I gave the AI:* `planning.md` Documents, Chunking Strategy, and Architecture build-time sections.
- *What it produced:* `chunk_documents.py` with two-stage delimiter + paragraph sub-splitting, metadata headers on each chunk, and stats/sample printing.
- *What I changed or overrode:* Verified chunk labels and plot sub-splits manually; adjusted testing output to inspect Wikipedia chunks; later removed duplicate Letterboxd `Common Themes` sections from the corpus after seeing retrieval noise.

**Instance 2 — Embedding, retrieval, generation, and UI (Milestones 4–5)**

- *What I gave the AI:* Retrieval Approach, Architecture query path, grounding requirements, and the Gradio skeleton from the assignment.
- *What it produced:* `embed_and_retrieve.py` (MiniLM + ChromaDB), `query.py` (Groq `ask()` with strict system prompt), and `app.py` (Gradio UI with programmatic sources).
- *What I changed or overrode:* Fixed Gradio `show_download_button` incompatibility (removed; used `buttons=[]`); ran all 5 eval questions and documented failures honestly in this README rather than tuning until results looked perfect.

---

## Demo Video

Record a 3–5 minute walkthrough showing: (1) at least 3 queries with sources visible, (2) one query that works well (e.g., Luke Hobbs), (3) one query that struggles (e.g., worldwide box office), and (4) this evaluation report. Run with `python app.py` → http://localhost:7860.
