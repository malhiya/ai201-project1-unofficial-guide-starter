"""Embedding + Vector Store and Retrieval stages of the RAG pipeline.

This file implements stages [3] and [4] from the Architecture diagram in
planning.md:

  [3] EMBEDDING + VECTOR STORE
      Encode each chunk into a vector, store with metadata.
      Tools: sentence-transformers (all-MiniLM-L6-v2) -> ChromaDB

  [4] RETRIEVAL                         <-- User query
      Embed query, similarity search        (embedded with the same model)
      Return top-k = 5 chunks
      Tool: ChromaDB

It loads chunks from the ingestion pipeline (ingest.py), embeds them with
all-MiniLM-L6-v2, and stores them in a persistent ChromaDB collection with
source metadata (source document name + the chunk's position in that document)
so retrieved answers can be attributed back to the student source they came
from.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import load_documents, chunk_document

# --- Retrieval Approach (planning.md) ---------------------------------------
# Embedding model: all-MiniLM-L6-v2 via sentence-transformers. It runs locally
# with no API key and no rate limits, which is why it's the default here.
# Top-k: 5 chunks per query (k=4 or k=5 is a sensible starting point — too few
# and the relevant chunk may be missing, too many and loosely related text
# dilutes the context and pulls the LLM off-target). Tune after seeing results.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# Where ChromaDB persists its index on disk. This folder is git-ignored.
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "unofficial_guide"

# Load the embedding model once at import time so we don't re-load it for every
# chunk batch or every query. The query and the stored chunks MUST use the same
# model for similarity search to be meaningful.
_model = SentenceTransformer(EMBEDDING_MODEL)


def build_chunks():
    """Run the ingestion pipeline and return a flat list of chunk dicts.

    Each chunk dict has "text", "topic", and "chunk_id" from ingest.py, plus:
      - "filename" : the source document the chunk came from
      - "position" : the chunk's 0-based index within that document
    """
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        doc_chunks = chunk_document(doc["text"], doc["topic"])
        # Record where each chunk sits within its source document. This is the
        # "position" half of the source metadata used for attribution later.
        for position, chunk in enumerate(doc_chunks):
            chunk["filename"] = doc["filename"]
            chunk["position"] = position
        all_chunks.extend(doc_chunks)
    print(f"Created {len(all_chunks)} chunk(s) across {len(docs)} document(s).")
    return all_chunks


def embed_texts(texts):
    """[3] EMBEDDING — encode a list of strings into vectors.

    Uses all-MiniLM-L6-v2 (384-dim sentence embeddings). Returns a plain list
    of vectors so they can be handed straight to ChromaDB.
    """
    embeddings = _model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def build_index():
    """[3] VECTOR STORE — embed every chunk and store it in ChromaDB.

    Stores each chunk's vector alongside its source metadata (source document
    name + position in that document) so retrieval can cite where the text came
    from. The collection is rebuilt from scratch each run so re-ingesting after
    editing documents/ or the chunking settings can't leave stale vectors
    behind.

    Returns the populated ChromaDB collection.
    """
    chunks = build_chunks()

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Drop any existing collection so we always index the current corpus.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    # Cosine distance matches how sentence-transformers embeddings are compared.
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "topic": chunk["topic"],
            "filename": chunk["filename"],
            "position": chunk["position"],
            "chunk_id": chunk["chunk_id"],
        }
        for chunk in chunks
    ]
    embeddings = embed_texts(documents)

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"Indexed {collection.count()} chunk(s) into '{COLLECTION_NAME}'.")
    return collection


def get_collection():
    """Open the persisted ChromaDB collection without re-indexing.

    Use this from the generation/interface stage once build_index() has been
    run at least once. Raises if the collection doesn't exist yet.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection(COLLECTION_NAME)


def retrieve(query, collection=None, top_k=TOP_K):
    """[4] RETRIEVAL — embed the query and return the top-k most similar chunks.

    The query is embedded with the SAME model used for the chunks, then
    ChromaDB does the similarity search. Returns a list of result dicts, each
    with the chunk "text", its source information (topic / filename / position),
    and the similarity "distance" (lower = closer for cosine).
    """
    if collection is None:
        collection = get_collection()

    query_embedding = _model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    # ChromaDB returns parallel lists wrapped in an outer list (one per query).
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved = []
    for text, meta, distance in zip(documents, metadatas, distances):
        retrieved.append({
            "text": text,
            "topic": meta["topic"],
            "filename": meta["filename"],
            "position": meta["position"],
            "chunk_id": meta["chunk_id"],
            "distance": distance,
        })
    return retrieved


if __name__ == "__main__":
    # Build the index, then run several evaluation-plan queries (planning.md)
    # so you can eyeball whether retrieval surfaces relevant chunks.
    collection = build_index()

    eval_queries = [
        "Which CS professor do students recommend, and why?",
        "Which dining hall is best for healthy eating?",
        "I don't like big crowds or noise — which residential area should I avoid?",
    ]

    for query in eval_queries:
        print("\n" + "=" * 70)
        print(f"Query: {query}")
        print(f"Top {TOP_K} retrieved chunk(s):")
        for i, result in enumerate(retrieve(query, collection), start=1):
            print("-" * 70)
            print(
                f"{i}. [{result['chunk_id']}] ({result['topic']}, "
                f"chunk #{result['position']}) — distance {result['distance']:.4f}"
            )
            print(result["text"])
