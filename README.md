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

**441 chunks** across all 10 files 

---

## Embedding Model

**Model used:**

`all-MiniLM-L6-v2` via `sentence-transformers`. 

**Production tradeoff reflection:**

With no cost constraint, I would weigh: (1) **context length** — a model supporting longer inputs would reduce need for aggressive plot sub-splitting; (2) **domain accuracy** — a larger model  may better match casual queries like "most money worldwide" to the right film; (3) **latency** — local MiniLM is fast, but API-hosted models add network cost; (4) **multilingual support** — not useful for this English-only corpus. 

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

Sources are **programmatic**, not LLM-generated. After retrieval, `format_sources()` builds a deduplicated list from chunk metadata (e.g., `wikipedia.txt — Fast Five / Cast`) and the Gradio UI displays them in a separate "Retrieved from" panel. 

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which movie introduced Luke Hobbs, and who plays him? | *Fast Five* (2011); Dwayne Johnson as DSS agent Luke Hobbs (`imdb.txt`, `wikipedia.txt`, `reddit.txt`) | Fast Five (2011); Dwayne Johnson. Top chunks: `wikipedia.txt` Franchise Notes, `imdb.txt` Casting Notes/Trivia. | Relevant | Accurate |
| 2 | Why is *Tokyo Drift* placed later in the franchise timeline despite being the third film released? | Release order is 3rd, but story chronology places it later (after *F6* events); Han's arc connects to later films (`wikipedia.txt`, `reddit.txt`, `screen_rant.txt`) | Mentioned release order vs. internal chronology and F6 retcon, but hedged that docs "do not explicitly state why." Retrieved timeline chunks from `wikipedia.txt` and `screen_rant.txt`. | Partially relevant | Partially accurate |
| 3 | Which Fast & Furious film earned the most money worldwide? | *Furious 7* — approximately $1.515 billion worldwide (`box_office_mojo.txt`, `the_numbers.txt`) | Incorrectly answered *The Fast and the Furious* (2001) at $207.5M. Retrieval returned per-film `## Revenue` chunks for FF1 and Tokyo Drift; Furious 7 `## Performance` ("highest-grossing worldwide") ranked outside top-k=5. | Partially relevant | Inaccurate |
| 4 | Which film changed the franchise from street racing into a heist/action series? | *Fast Five* — Rio heist, vault chase, ensemble crew template (`wikipedia.txt`, `screen_rant.txt`, `roger_ebert.txt`) | Fast Five (2011) pivoted from street racing to heist action. Top chunks: `wikipedia.txt` Production, `imdb.txt` Production Facts. | Relevant | Accurate |
| 5 | How did critics and fans react to *F9*? | Polarized: critics mixed (Tomatometer ~59%); fans split — space/magnet scene mocked, Han's return celebrated (`rotten_tomatoes.txt`, `letterboxd.txt`, `reddit.txt`) | Captured fan negativity on Reddit and audience/critic score gap, but missed Tomatometer ~59% and space-magnet mockery. Retrieved fan/review chunks, not `## Critic Consensus`. | Partially relevant | Partially accurate |


**Summary:** 2 accurate, 2 partially accurate, 1 inaccurate on the 5 planned questions. 

---

## Failure Case Analysis

**Question that failed:**

Who plays Letty?

**What the system returned:**

The system said the documents do not mention who plays Letty — even though `wikipedia.txt` and `imdb.txt` `## Cast` / `## Casting Notes` chunks explicitly list **Michelle Rodriguez as Letty Ortiz**.

**Root cause (tied to a specific pipeline stage):**

**Retrieval (embedding + top-k search).** The query matched plot chunks that *mention* Letty as a character (distances **0.61–0.63**, all above the 0.5 weak-match threshold) instead of cast-list chunks that pair her name with the actor. MiniLM treats "Who plays Letty?" as who "tricked" Letty rather than who plays her character. I demonstrate this in the video by slightly changing the wording of the question to "who is the actress that plays Letty" (it pulls the correct chunks). It could also be that the chunk that reveals who she is played by is not being capture with our top-k of 5.  

**What you would change to fix it:**

Change the wording of the question or increase K to 5. 
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

