"""Temporary script to run all 5 eval questions for README documentation."""
from embed_and_retrieve import retrieve
from query import ask

QUESTIONS = [
    "Which movie introduced Luke Hobbs, and who plays him?",
    "Why is Tokyo Drift placed later in the franchise timeline despite being the third film released?",
    "Which Fast & Furious film earned the most money worldwide?",
    "Which film changed the franchise from street racing into a heist/action series?",
    "How did critics and fans react to F9?",
]

for i, q in enumerate(QUESTIONS, 1):
    print("=" * 80)
    print(f"Q{i}: {q}")
    hits = retrieve(q, k=5)
    print("RETRIEVAL:")
    for j, h in enumerate(hits, 1):
        m = h.metadata
        print(f"  {j}. [{m['source_file']}] {m['movie']} / {m['section']} dist={h.distance:.3f}")
    result = ask(q)
    print("ANSWER:", result["answer"])
    print("SOURCES:")
    for s in result["sources"]:
        print(f"  • {s}")
    print()
