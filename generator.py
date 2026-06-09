"""Generation stage of the RAG pipeline.

This file implements stage [5] from the Architecture diagram in planning.md:

  [5] GENERATION
      Build a prompt from the retrieved chunks, generate a grounded answer.
      Tool: Groq LLM (llama-3.3-70b-versatile)

It connects retrieval (retriever.py) to the LLM: it retrieves the top-k chunks
for a question, packs them into a prompt as the ONLY allowed source of truth,
and asks Groq's llama-3.3-70b-versatile to answer from that context alone. The
model is instructed to say it doesn't know when the context doesn't cover the
question, which is what keeps answers grounded instead of hallucinated.
"""

from groq import Groq

from config import GROQ_API_KEY
from retriever import retrieve, TOP_K

# Groq's free-tier, OpenAI-compatible llama-3.x model (see planning.md diagram).
LLM_MODEL = "llama-3.3-70b-versatile"

# One client, initialized from the GROQ_API_KEY loaded out of .env by config.py.
_client = Groq(api_key=GROQ_API_KEY)

# The grounding contract. The model must answer ONLY from the provided context
# and must refuse to guess — this is what makes eval question 5 (meal-plan cost,
# which no document covers) correctly return "I don't know."
SYSTEM_PROMPT = (
    "You are The Unofficial Guide, a helpful assistant that answers questions "
    "about UMass Amherst using ONLY student-generated knowledge provided to you "
    "as context (Reddit threads, Rate My Professor reviews, CICS pages).\n\n"
    "Rules:\n"
    "1. Answer using ONLY the information in the provided context. Do not use "
    "any outside knowledge.\n"
    "2. If the context does not contain enough information to answer, say so "
    "plainly: \"I don't know — the sources I have don't cover that.\" Do not "
    "guess or invent details.\n"
    "3. Cite the source(s) you used inline by their topic name when relevant.\n"
    "4. Keep the answer concise and grounded in what students actually said."
)


def build_prompt(query, chunks):
    """Build the user prompt: the retrieved chunks as context + the question.

    Each chunk is labeled with its source (topic + document name) so the model
    can attribute claims and so the context boundaries are explicit.
    """
    context_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        context_blocks.append(
            f"[Source {i}: {chunk['topic']} ({chunk['filename']})]\n{chunk['text']}"
        )
    context = "\n\n".join(context_blocks)

    return (
        f"Context from student sources:\n\n{context}\n\n"
        f"---\n"
        f"Question: {query}\n\n"
        f"Answer using only the context above. If the context doesn't cover it, "
        f"say you don't know."
    )


def format_sources(chunks):
    """Return a deduplicated list of sources for attribution (topic + filename).

    Multiple retrieved chunks often come from the same document; we collapse
    them so the answer shows each source once, in retrieval order.
    """
    sources = []
    seen = set()
    for chunk in chunks:
        key = chunk["filename"]
        if key not in seen:
            seen.add(key)
            sources.append({"topic": chunk["topic"], "filename": chunk["filename"]})
    return sources


def generate_answer(query, top_k=TOP_K):
    """[5] GENERATION — retrieve context, then generate a grounded answer.

    Returns a tuple (answer, sources):
      - answer  : the LLM's grounded response (str)
      - sources : deduplicated list of {"topic", "filename"} dicts used as context

    If retrieval comes back empty (e.g. the index hasn't been built), we skip
    the LLM call and report that directly rather than letting it hallucinate.
    """
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return ("I don't know — no sources are available to answer from.", [])

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(query, chunks)},
        ],
        temperature=0.2,  # low temperature: stay close to the source text
    )
    answer = response.choices[0].message.content.strip()
    return answer, format_sources(chunks)


if __name__ == "__main__":
    # Smoke-test generation against the evaluation-plan queries (planning.md),
    # including question 5 which no document covers (should answer "I don't know").
    eval_queries = [
        "Which CS professor do students recommend, and why?",
        "Which dining hall is best for healthy eating?",
        "How much does a UMass student meal plan cost per semester?",
    ]
    for query in eval_queries:
        print("\n" + "=" * 70)
        print(f"Q: {query}")
        answer, sources = generate_answer(query)
        print(f"\nA: {answer}")
        print("\nSources:")
        for s in sources:
            print(f"  - {s['topic']} ({s['filename']})")
