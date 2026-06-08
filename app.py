from pathlib import Path

import gradio as gr

from query import ask

ASSETS_DIR = Path(__file__).parent / "assets"
HEADER_CANDIDATES = ("header.png", "header.jpg", "header.jpeg", "header.webp")


def find_header_image() -> Path | None:
    """Return the first matching header image in assets/ (add one of these filenames)."""
    for name in HEADER_CANDIDATES:
        path = ASSETS_DIR / name
        if path.exists():
            return path
    return None


def handle_query(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown("# The Unofficial Guide — Fast & Furious")

    header_image = find_header_image()
    if header_image:
        gr.Image(
            value=str(header_image),
            interactive=False,
            show_label=False,
            buttons=[],
            container=False,
            height=240,
        )

    gr.Markdown("Ask questions about the franchise. Answers use only retrieved documents.")

    inp = gr.Textbox(label="Your question", placeholder="Which movie introduced Luke Hobbs?")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
