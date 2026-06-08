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

**Chunk size:** One chunk per `##` section, prefixed with its `=== MOVIE:` header (`YEAR`, `SOURCE`, `SOURCE_URL`). Average **~215 characters** (~55 tokens); largest sections **~375 characters** — well under the **~800-token** sub-split threshold, so paragraph splitting is rarely needed. Target **~330 chunks** total across all 10 files.

**Overlap:** **0 characters** — no overlap. Sections are self-contained (e.g., `## Plot`, `## Fan Opinions`, `## Revenue`).

**Reasoning:** The corpus mixes short factual sections (box office figures) and opinion summaries (Letterboxd, Reddit). Chunking on `=== MOVIE:` then `##` keeps each unit topically coherent — a question about Hobbs retrieves `## Casting Notes` or `## Franchise Analysis`, not a unrelated film's plot. Fixed character windows would split mid-fact (e.g., separating budget from worldwide gross). Preprocessing strips the file-level `CORPUS:` header and attaches metadata (`movie`, `year`, `source`, `source_url`, `section`) to every chunk for citations.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which movie introduced Luke Hobbs, and who plays him? | *Fast Five* (2011); Dwayne Johnson as DSS agent Luke Hobbs (`imdb.txt`, `wikipedia.txt`, `reddit.txt`) |
| 2 | Why is *Tokyo Drift* placed later in the franchise timeline despite being the third film released? | Release order is 3rd, but story chronology places it later (after *F6* events); Han's arc connects to later films (`wikipedia.txt`, `reddit.txt`, `screen_rant.txt`) |
| 3 | Which Fast & Furious film earned the most money worldwide? | *Furious 7* — approximately $1.515 billion worldwide (`box_office_mojo.txt`, `the_numbers.txt`) |
| 4 | Which film changed the franchise from street racing into a heist/action series? | *Fast Five* — Rio heist, vault chase, ensemble crew template (`wikipedia.txt`, `screen_rant.txt`, `roger_ebert.txt`) |
| 5 | How did critics and fans react to *F9*? | Polarized: critics mixed (Tomatometer ~59%); fans split — space/magnet scene mocked, Han's return celebrated (`rotten_tomatoes.txt`, `letterboxd.txt`, `reddit.txt`) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Duplicate content across sources** — plot on Wikipedia and franchise analysis on Screen Rant may retrieve together and crowd out niche facts (timeline, box office). Mitigation: metadata filtering by section type for factual queries.

2. **Comparison queries** — "critics vs fans on *Fast Five*" may retrieve chunks from only one perspective if top-k is too low. Mitigation: raise k or retrieve per-source then merge.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
