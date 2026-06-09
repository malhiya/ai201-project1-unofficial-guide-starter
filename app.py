"""Query interface for the RAG pipeline.

This file implements stage [6] from the Architecture diagram in planning.md:

  [6] INTERFACE
      User asks questions, sees the answer + the sources it came from.
      Tool: Gradio

It wraps generator.generate_answer() in a minimal Gradio web UI: a textbox for
the question, an "Ask" button, and two output boxes — the grounded answer and
the list of student sources the answer was drawn from (attribution).
"""

import gradio as gr

from generator import generate_answer


def handle_query(question):
    """Run one question through the pipeline and format it for the UI.

    Returns (answer_text, sources_text). generate_answer() gives back a
    deduplicated list of {"topic", "filename"} dicts, which we render as a
    simple bulleted list so the user can see where the answer came from.
    """
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    answer, sources = generate_answer(question)
    sources_text = "\n".join(
        f"• {s['topic']} ({s['filename']})" for s in sources
    )
    return answer, sources_text


with gr.Blocks(title="The Unofficial Guide — UMass Amherst") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about UMass Amherst — professors, dorms, dining, clubs, CS advice. "
        "Answers come only from student sources (Reddit, Rate My Professor, CICS)."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Which CS professor do students recommend?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
