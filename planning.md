# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
This domain covers fan and audience opinions on the Fast & Furious franchise—how viewers rank each installment, what they praise or criticize, and how the series evolved from street racing to insane heists. That knowledge is valuable because watch-order confusion, wildly mixed reception, and long-running inside jokes make it hard to know where to start or which films are worth your time. Official channels (trailers, press, aggregate critic scores) flatten those nuances; real sentiment lives scattered across hundreds of individual Metacritic user reviews that no studio page summarizes.


---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

Corpus is organized **one review platform per file**; each file has sections for 10 mainline Fast and Furious films (2001–2023). Together the sources mix **audience** (Metacritic users, IMDb, Letterboxd), **professional critics** (Roger Ebert, IGN, Empire), **aggregators** (Rotten Tomatoes, Metacritic critics, Wikipedia), and **fan-culture editorial** (ScreenRant).

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Metacritic — User Reviews | Scored fan reviews (0–10) across all 10 films; captures polarized audience takes, franchise ranking debates, and which entries fans love or hate | https://www.metacritic.com/ · `documents/source_01_metacritic_user.txt` |
| 2 | IMDb — User Reviews | Long-form fan reviews per film; practical watch advice, nostalgia, and informal consensus on cast chemistry and rewatch value | https://www.imdb.com/ · `documents/source_02_imdb_user.txt` |
| 3 | Rotten Tomatoes — Critics & Audience | Tomatometer scores and critic-aggregation context per film; shows where professional consensus diverges from fan enthusiasm | https://www.rottentomatoes.com/ · `documents/source_03_rottentomatoes.txt` |
| 4 | Wikipedia — Critical Response | Summarized reception and box-office context from each film's Wikipedia page; useful for broad critical narrative and franchise milestones | https://en.wikipedia.org/wiki/Fast_%26_Furious · `documents/source_04_wikipedia.txt` |
| 5 | Metacritic — Critic Reviews | Professional critic scores (0–100) per film; complements user reviews to compare critic vs. audience gaps (e.g., *Fast Five* praised by critics, divisive among fans) | https://www.metacritic.com/ · `documents/source_05_metacritic_critic.txt` |
| 6 | ScreenRant | Editorial and fan-culture articles: franchise rankings, iconic scenes (tank chase, space magnets, Dom's son leap), Paul Walker tribute, and "jumped the shark" debates | https://screenrant.com/ · `documents/source_06_screenrant.txt` |
| 7 | IGN | Professional entertainment reviews per film; structured critic takes on action quality, story, and how each entry fits the evolving franchise formula | https://www.ign.com/ · `documents/source_07_ign.txt` |
| 8 | RogerEbert.com | Roger Ebert / RogerEbert.com critic reviews with star ratings across all 10 films; established critical voice on whether each installment works as filmmaking vs. spectacle | https://www.rogerebert.com/ · `documents/source_08_rogerebert.txt` |
| 9 | Empire Online | UK film-magazine reviews per installment; international critic perspective on action craft, cast, and franchise reinvention (*Tokyo Drift* through *Fast X*) | https://www.empireonline.com/ · `documents/source_09_empire_online.txt` |
| 10 | Letterboxd — Community Reviews | Film-diary community consensus per title; cinephile/fan sentiment, meme culture, and how engaged viewers rank entries in watch order | https://letterboxd.com/ · `documents/source_10_letterboxd.txt` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** ~500–650 characters per chunk on average; hard cap of **1,000 characters**  when a single review must be sub-split. Target **~120–130 chunks** total across all 10 source files.

**Overlap:** **0 characters** — no overlap between chunks. I've pre-processed the documents to use delimiters as well as stripped unrelated noise to allow for better accuracy when chunking / embedding.

**Reasoning:** The corpus is review-heavy, each file is organized into `=== Film Title ===` sections with one or more discrete `REVIEW` blocks (Metacritic user files bundle 2 reviews per film; Metacritic critic files bundle 3 critic blurbs per film; other sources have 1 review per film). Chunking on `REVIEW` boundaries keeps each unit semantically whole — one opinion with its score, source, and film title — which matters for questions like "what do fans think of *Tokyo Drift*?" vs. "how did critics rate *Fast Five*?". Analysis of the files shows median chunk size ~560 characters and only a handful of outliers above 1,500 characters (long Metacritic user rants), so fixed-size sliding windows would either mash unrelated reviews together or cut mid-sentence through scored opinions. Each chunk will prepend the film header and source metadata (URL, rating scale) for attribution. Preprocessing strips the shared file header (lines 1–7) before chunking since it repeats across every section in a file.

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
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

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
