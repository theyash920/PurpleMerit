"""
Configuration module for the Agentic RAG Course Planning Assistant.
Centralizes all settings: API keys, model names, paths, and retrieval parameters.
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ─── API Keys ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ─── LLM Configuration ──────────────────────────────────────────────────────
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 4096

# ─── Embedding Configuration ────────────────────────────────────────────────
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# ─── Vector Store ────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")
CHROMA_COLLECTION_NAME = "stanford_catalog"

# ─── Data Paths ──────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
COURSES_DIR = os.path.join(DATA_DIR, "courses")
PROGRAMS_DIR = os.path.join(DATA_DIR, "programs")
POLICIES_DIR = os.path.join(DATA_DIR, "policies")

# ─── Retrieval Parameters ───────────────────────────────────────────────────
RETRIEVAL_K_COURSES = 3       # Top-k for course-specific queries
RETRIEVAL_K_PROGRAMS = 5      # Top-k for program/policy queries
RETRIEVAL_K_DEFAULT = 5       # Default top-k
RERANK_CANDIDATES = 10        # Fetch this many candidates before re-ranking

# ─── Output ──────────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
