# Agentic RAG Challenge Implementation Plan (Advanced Version)

## 1. Data Requirements
- Use Stanford University's public catalog (20 courses, 2 programs, 1 policy).
- Enriched data with prerequisite logic, co-requisites, minimum grades, offered terms.
- `sources.md` tracks all URLs and access dates.
- **Target: 30,000+ words** across all documents.

---

## 2. Advanced RAG Pipeline Architecture

### Document Ingestion & Structure-Aware Chunking
- **Course files:** Each course = 1 chunk (preserves full prerequisite logic).
- **Program/Policy files:** Split on section headers (e.g., REQUIREMENTS, GRADING SCALE).
- **Rich Metadata on every chunk:** `title`, `source_url`, `section_name`, `doc_type`, `prerequisites`, `min_grade`.

### Embeddings & Hybrid Retrieval
- **Embeddings Model:** `BAAI/bge-base-en-v1.5` (open-source, via SentenceTransformers).
- **Vector Store:** ChromaDB (local, persistent).
- **Hybrid Retrieval with Dynamic k:**
  - Course queries: semantic search + `doc_type=course` filter, `k=3`.
  - Program queries: semantic search + `doc_type=program` filter, `k=5-7`.
  - Policy queries: semantic search + `doc_type=policy` filter, `k=5`.
- **Re-ranking:** Fetch top-10 candidates, re-rank via Groq LLM scoring, return top-k.

---

## 3. Agentic Design (CrewAI + Groq)

### Agent 1: Intake Agent
- Parses student query, checks for missing info (major, grades, term).
- Outputs 1-5 clarifying questions if info is incomplete.

### Agent 2: Catalog Retriever Agent
- Executes hybrid retrieval + re-ranking pipeline.
- Returns exact text chunks with URL metadata.

### Agent 3: Planner Agent
- Reasons ONLY over retrieved context (no prior knowledge leakage).
- Hidden `<reasoning_trace>` for chain-of-thought debugging.
- Safe abstention: "I don't have that information in the provided catalog/policies."

### Agent 4: Verifier Agent
- Enforces mandatory output format.
- Minimum evidence threshold: at least 1 citation per claim.
- Blocks/rewrites output if grounding is weak.

---

## 4. Mandatory Output Format
```
Answer / Plan: [Decision or Suggested List]
Why (requirements/prereqs satisfied): [Reasoning based on text]
Citations: [Exact URL + heading/chunk id from metadata]
Clarifying questions (if needed): [1-5 questions, or N/A]
Assumptions / Not in catalog: [Assumptions made, or "I don't have that information..."]
```

---

## 5. Evaluation Strategy (25 Queries)
- 10 prerequisite checks (eligible / not eligible).
- 5 multi-hop chain questions (needs 2+ courses of evidence).
- 5 program requirement questions.
- 5 trick / "not-in-docs" questions.

### Metrics:
- Citation Coverage Rate
- Abstention Accuracy
- Precision@k and Recall@k (retrieval-level)
- Eligibility Correctness

---

## 6. Tech Stack Summary
- **LLM:** Groq API (`llama-3.3-70b-versatile`)
- **Embeddings:** `BAAI/bge-base-en-v1.5` (HuggingFace, free)
- **Vector Store:** ChromaDB (local)
- **Framework:** CrewAI
- **Language:** Python

---

## 7. File Structure
```
Agentic-RAG-using-Crew-AI/
├── config.py          # All settings, API keys, paths
├── ingest.py          # Document loading + chunking + vectorstore
├── retriever.py       # Hybrid retrieval + re-ranking
├── agents.py          # CrewAI agent definitions (4 agents)
├── tasks.py           # CrewAI task definitions
├── crew.py            # Crew assembly + execution
├── evaluate.py        # 25-query evaluation framework
├── main.py            # CLI entry point
├── requirements.txt   # Dependencies
├── README.md          # Setup & run instructions
├── data/
│   ├── courses/       # 20 course .txt files
│   ├── programs/      # 2 program .txt files
│   ├── policies/      # 1 policy .txt file
│   └── sources.md     # URL tracking
├── vectorstore/       # ChromaDB persistent storage
└── results/           # Evaluation outputs
```
