# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
This domain covers **unofficial Fast & Furious franchise knowledge** — plot and characters, timeline/watch-order confusion, critical and fan reception, box-office performance, production trivia, and how the series evolved from street racing to globe-trotting heist blockbusters. That knowledge is valuable because Universal's official marketing doesn't explain *Tokyo Drift*'s timeline placement, which entry introduced Luke Hobbs, why Han is a fan favorite, or where critics and audiences disagree. Real answers live scattered across Wikipedia, fan forums, review aggregators, and editorial retrospectives — no single studio page ties it together.


---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

Corpus is organized **one source type per file**; each file has `=== MOVIE:` blocks for all 10 mainline films (2001–2023) with `##` subsections. Sources mix **reference** (Wikipedia), **financial** (Box Office Mojo, The Numbers), **critics** (Rotten Tomatoes, Metacritic, Roger Ebert), **fan culture** (Letterboxd, Reddit), **production trivia** (IMDb), and **franchise editorial** (Screen Rant).

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Wikipedia | Plot, cast, production, release, reception, timeline notes per film | https://en.wikipedia.org/wiki/Fast_%26_Furious · `documents/wikipedia.txt` |
| 2 | Rotten Tomatoes | Tomatometer, critic consensus, audience reaction, review highlights | https://www.rottentomatoes.com/m/fast_five · `documents/rotten_tomatoes.txt` |
| 3 | Metacritic | Critic/user score context, professional and fan review summaries | https://www.metacritic.com/movie/fast-five/ · `documents/metacritic.txt` |
| 4 | IMDb | Trivia, production facts, casting notes (e.g., Hobbs debut in *Fast Five*) | https://www.imdb.com/title/tt1596343/ · `documents/imdb.txt` |
| 5 | Box Office Mojo | Worldwide/domestic/intl gross, opening weekend, franchise rankings | https://www.boxofficemojo.com/title/tt2820852/ · `documents/box_office_mojo.txt` |
| 6 | The Numbers | Budget, revenue, profitability analysis per film | https://www.the-numbers.com/ · `documents/the_numbers.txt` |
| 7 | Letterboxd | Positive/negative fan reactions, common themes | https://letterboxd.com/film/fast-five/ · `documents/letterboxd.txt` |
| 8 | Reddit | Fan opinions, character/timeline/ranking threads (r/fastandfurious, r/movies) | https://www.reddit.com/r/fastandfurious/ · `documents/reddit.txt` |
| 9 | RogerEbert.com | Professional review summaries, praise, criticism with star ratings | https://www.rogerebert.com/reviews/fast-five-2011 · `documents/roger_ebert.txt` |
| 10 | Screen Rant | Franchise analysis, character notes, timeline explainers, rankings | https://screenrant.com/fast-five-best-franchise/ · `documents/screen_rant.txt` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Two-stage chunking:**

1. **Primary split (delimiter-based):** One chunk per `##` section, prefixed with its `=== MOVIE:` header (`YEAR`, `SOURCE`, `SOURCE_URL`). This yields **~322 sections** across all 10 files.
2. **Sub-split (size-based, only when needed):** If a section exceeds **500 characters** (~125 tokens), split it on paragraph boundaries (`\n\n`) into smaller pieces. Group paragraphs until the next one would push the chunk over 500 chars, then start a new sub-chunk. Only Wikipedia `## Plot` sections need this today (10 sections, **~2,700–4,300 characters** each).

**Final chunk size:** Most chunks stay small (**~50–375 characters** for Cast, box office, Reddit comments, etc.). Sub-split plot chunks target **~400–500 characters** (~100–125 tokens), safely under `all-MiniLM-L6-v2`'s **256-token** limit. Target **~380 chunks** total after sub-split.

**Overlap:** **0 characters** between different `##` sections. **1 paragraph overlap** between sub-chunks *within* the same section — the last paragraph of sub-chunk 1 repeats as the first paragraph of sub-chunk 2, so plot beats at a boundary aren't lost.

**Reasoning:** Delimiter chunking keeps each unit topically coherent — a Hobbs question retrieves `## Casting Notes`, not an unrelated film's plot. Fixed character windows would split mid-fact (e.g., separating budget from worldwide gross). Full Wikipedia plots made primary `## Plot` sections too large for MiniLM to embed whole; sub-splitting by paragraph fixes that without changing the file format. Preprocessing strips the file-level `CORPUS:` header and attaches metadata (`movie`, `year`, `source`, `source_url`, `section`, `sub_chunk`) to every chunk for citations.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 (free)
**Top-k:**
5 (to ensure at least some context)
**Production tradeoff reflection:**
I'd choose an embedding model that allows for longer conext embedding
Don't think multilingual support would be particularly useful
I'd ingest more sources as more sources might corroborate with more accuracy but that introduces more latency and noise most likely. 

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which movie introduced Luke Hobbs, and who plays him? | *Fast Five* (2011); Dwayne Johnson as DSS agent Luke Hobbs (`imdb.txt`, `wikipedia.txt`, `reddit.txt`) | Fast Five (2011); Dwayne Johnson. Top chunks: `wikipedia.txt` Franchise Notes, `imdb.txt` Casting Notes/Trivia. | Relevant | Accurate |
| 2 | Why is *Tokyo Drift* placed later in the franchise timeline despite being the third film released? | Release order is 3rd, but story chronology places it later (after *F6* events); Han's arc connects to later films (`wikipedia.txt`, `reddit.txt`, `screen_rant.txt`) | Mentioned release order vs. internal chronology and F6 retcon, but hedged that docs "do not explicitly state why." Retrieved timeline chunks from `wikipedia.txt` and `screen_rant.txt`. | Partially relevant | Partially accurate |
| 3 | Which Fast & Furious film earned the most money worldwide? | *Furious 7* — approximately $1.515 billion worldwide (`box_office_mojo.txt`, `the_numbers.txt`) | Incorrectly answered *The Fast and the Furious* (2001) at $207.5M. Retrieval returned per-film `## Revenue` chunks for FF1 and Tokyo Drift; Furious 7 `## Performance` ("highest-grossing worldwide") ranked outside top-k=5. | Partially relevant | Inaccurate |
| 4 | Which film changed the franchise from street racing into a heist/action series? | *Fast Five* — Rio heist, vault chase, ensemble crew template (`wikipedia.txt`, `screen_rant.txt`, `roger_ebert.txt`) | Fast Five (2011) pivoted from street racing to heist action. Top chunks: `wikipedia.txt` Production, `imdb.txt` Production Facts. | Relevant | Accurate |
| 5 | How did critics and fans react to *F9*? | Polarized: critics mixed (Tomatometer ~59%); fans split — space/magnet scene mocked, Han's return celebrated (`rotten_tomatoes.txt`, `letterboxd.txt`, `reddit.txt`) | Captured fan negativity on Reddit and audience/critic score gap, but missed Tomatometer ~59% and space-magnet mockery. Retrieved fan/review chunks, not `## Critic Consensus`. | Partially relevant | Partially accurate |

**Summary:** 2 accurate, 2 partially accurate, 1 inaccurate on the 5 planned questions (matches README Evaluation Report).

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Duplicate content across sources** — plot on Wikipedia and franchise analysis on Screen Rant may retrieve together and crowd out niche facts (timeline, box office). 

2. **The nature of user contrbutions on platforms like Reddit could introduce off-topic retrieval or inaccurate information** — 
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
BUILD-TIME 
===================

documents/*.txt
      |
      v
+------------------+     +------------------+     +------------------+
| 1. Ingestion     | --> | 2. Chunking      | --> | 3. Embedding     |
| Python (pathlib) |     | Python split     |     | all-MiniLM-L6-v2 |
| load + clean     |     | === MOVIE: / ##  |     | text -> vectors  |
+------------------+     +------------------+     +------------------+
                                                        |
                                                        v
                                                 +------------------+
                                                 | 4. Vector Store  |
                                                 | ChromaDB         |
                                                 | save vectors +   |
                                                 | metadata         |
                                                 +------------------+


QUERY-TIME 
=========================

User question
      |
      v
+------------------+     +------------------+     +------------------+
| 5. Retrieval     | --> | 6. Generation    | --> | Answer + sources |
| MiniLM embed Q   |     | Groq API         |     | (grounded, cited)|
| ChromaDB top-k   |     | llama-3.3-70b    |     |                  |
+------------------+     +------------------+     +------------------+
      ^
      |
 ChromaDB (search)
```

**Build-time (once):** load 10 corpus files → chunk `##` sections with metadata → embed → store in ChromaDB.

**Query-time (per question):** embed question → retrieve top-k chunks → Groq generates grounded answer with source filenames.

| Stage | Tool |
|-------|------|
| Ingestion | Python (`pathlib`) |
| Chunking | Python (delimiter split) |
| Embedding | `sentence-transformers` / `all-MiniLM-L6-v2` |
| Vector store | ChromaDB |
| Retrieval | MiniLM + ChromaDB |
| Generation | Groq API |

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I'll use Claude and give it my Documents, Chunking Strategy, and Architecture build-time sections. I expect a Python script that loads `documents/*.txt`, strips the `CORPUS:` header, and splits on `=== MOVIE:` and `##` with metadata on each chunk. I'll verify by printing 5 chunks and checking they are self-contained, correctly labeled, that long `## Plot` sections are sub-split, and total around 380.

**Milestone 4 — Embedding and retrieval:**

I'll use Claude and give it my Retrieval Approach, Architecture query path, and a sample chunk. I expect code that embeds chunks with `all-MiniLM-L6-v2`, stores them in ChromaDB, and retrieves top-k results for a query. I'll verify by running 3 eval questions and confirming returned chunks are on-topic with distance scores below 0.5.

**Milestone 5 — Generation and interface:**

I'll use Claude and give it my Architecture, Evaluation Plan, and grounding requirements from the assignment. I expect a Groq-backed `ask()` function with a strict context-only prompt plus a Gradio UI that shows answer and sources. I'll verify with 2 grounded answers that cite filenames, plus one out-of-scope question that refuses to answer.
