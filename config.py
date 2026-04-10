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

# Using llama-3.3-70b-versatile (12K TPM on free tier).
# Optimized for 12K TPM: 2-agent pipeline, no LLM rerank, compressed prompts.
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 300

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
RETRIEVAL_K_COURSES = 5       # Top-k for course-specific queries (need target + prereqs)
RETRIEVAL_K_PROGRAMS = 3      # Top-k for program/policy queries (reduced for TPM)
RETRIEVAL_K_DEFAULT = 5       # Default top-k
RERANK_CANDIDATES = 0         # 0 = disabled (no LLM rerank to save tokens)

# ─── Pipeline Settings ───────────────────────────────────────────────────────
SLIDING_WINDOW_SIZE = 3           # Only last N messages sent to LLM
CLASSIFIER_MAX_TOKENS = 80        # Classifier needs very few tokens
WORKER_MAX_TOKENS = 500           # Worker agents get more room for answers

# ─── Output ──────────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
