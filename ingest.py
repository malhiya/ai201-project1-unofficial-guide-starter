import os
from config import DOCS_PATH


def load_documents():
    """Load all .txt source documents from the documents folder.

    Each file in documents/ is one student-knowledge source (a Reddit thread,
    a Rate My Professor page, a CICS org/events page, etc.). The filename is
    turned into a readable topic name used later for source attribution, e.g.
    "dining-halls-reddit.txt" -> "Dining Halls Reddit".
    """
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            # Filenames use hyphens and underscores as word separators; both
            # become spaces so the topic reads naturally in citations.
            topic = (
                filename.replace(".txt", "")
                .replace("-", " ")
                .replace("_", " ")
                .title()
            )
            documents.append({
                "topic": topic,
                "filename": filename,
                "text": text,
            })
    print(f"Loaded {len(documents)} document(s): {[d['topic'] for d in documents]}")
    return documents


def chunk_document(text, topic):
    """
    Split a source document into chunks ready for embedding.

    Strategy: character-based sliding window with overlap.
      - chunk_size = 1200 characters: most of these documents are Reddit
        comment threads where individual comments run ~1,200 characters, so
        this is long enough to carry one full opinion/review as a unit while
        staying focused enough to return targeted results.
      - overlap = 200 characters (~17%): duplicates a small window of text at
        each boundary so a comment that spans two chunks can still be
        retrieved intact and keeps continuity across the boundary.
      - min_length = 100 characters: filters out whitespace artifacts and very
        short fragments (e.g. a trailing one-liner) that add noise without
        useful semantic content.

    These numbers match the Chunking Strategy section of planning.md. If you
    change them there, change them here too.

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "topic"    : the topic name, e.g. "Dining Halls Reddit" (str)
      - "chunk_id" : a unique identifier, e.g. "dining_halls_reddit_0" (str)
    """
    chunk_size = 500
    overlap = 100
    min_length = 100

    chunks = []
    prefix = topic.lower().replace(" ", "_")
    counter = 0

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if len(chunk_text) >= min_length:
            chunks.append({
                "text": chunk_text,
                "topic": topic,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1

        # Advance by (chunk_size - overlap) so the next chunk shares
        # `overlap` characters with the tail of this one.
        start += chunk_size - overlap

    return chunks


def print_sample_chunks(chunks, n=5):
    """Print the first n chunks so you can eyeball the chunking output."""
    print(f"\nShowing {min(n, len(chunks))} of {len(chunks)} chunk(s):")
    for chunk in chunks[:n]:
        print("-" * 70)
        print(f"[{chunk['chunk_id']}] ({chunk['topic']}) — {len(chunk['text'])} chars")
        print(chunk["text"])


if __name__ == "__main__":
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        doc_chunks = chunk_document(doc["text"], doc["topic"])
        all_chunks.extend(doc_chunks)
    print(f"Created {len(all_chunks)} chunk(s) across {len(docs)} document(s).")
    # print_sample_chunks(all_chunks, 5) #130 chunks with 500 char length and 100 overlap
