import os

from dotenv import load_dotenv

load_dotenv()

# Folder holding the .txt source documents (Reddit threads, Rate My Professor,
# CICS pages, etc.) that make up the UMass "unofficial guide" corpus.
DOCS_PATH = os.getenv("DOCS_PATH", "documents")

# Groq API key for the generation stage (Milestone 5). Loaded from .env.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
