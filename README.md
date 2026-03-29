# Prerequisite & Course Planning Assistant (Agentic RAG)

A **CrewAI-based Agentic RAG system** that answers student course-planning questions grounded strictly in Stanford University's academic catalog. Built for the Purple Merit Technologies Agentic RAG Challenge.

## Features

- **Grounded Answers with Citations** — Every claim is backed by a catalog URL
- **Prerequisite Reasoning** — Multi-hop prerequisite chain analysis
- **Course Plan Generation** — Suggests eligible courses based on completed coursework
- **Clarifying Questions** — Asks for missing info instead of guessing
- **Safe Abstention** — Refuses to answer when policy is not in the documents
- **4-Agent CrewAI Pipeline** — Intake → Retriever → Planner → Verifier

## Architecture

```
Student Query
     │
     ▼
┌─────────────┐
│ Intake Agent│ → Checks for missing info, asks clarifying questions
└──────┬──────┘
       ▼
┌──────────────────┐
│ Retriever Agent  │ → Hybrid search (semantic + metadata filter + LLM reranking)
└──────┬───────────┘
       ▼
┌──────────────┐
│ Planner Agent│ → Reasons strictly over retrieved context with CoT trace
└──────┬───────┘
       ▼
┌───────────────┐
│ Verifier Agent│ → Audits citations, enforces output format
└──────┬────────┘
       ▼
  Final Answer (with citations)
```

## Tech Stack

| Component     | Technology                          |
|--------------|-------------------------------------|
| LLM          | Groq API (Llama 3.3 70B)          |
| Embeddings   | BAAI/bge-base-en-v1.5 (HuggingFace)|
| Vector Store | ChromaDB                            |
| Framework    | CrewAI                              |
| Language     | Python 3.10+                        |

## Setup

### 1. Clone & Install
```bash
git clone <repo-url>
cd Agentic-RAG-using-Crew-AI
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Build the Vector Store
```bash
python main.py ingest
```

### 4. Ask a Question
```bash
python main.py ask "Can I take CS161 if I have completed CS106A and CS106B?"
```

### 5. Interactive Mode
```bash
python main.py interactive
```

### 6. Run Evaluation (25 queries)
```bash
python main.py evaluate
```

## Project Structure

```
├── config.py          # Configuration (API keys, models, paths)
├── ingest.py          # Document ingestion & structure-aware chunking
├── retriever.py       # Hybrid retrieval with LLM re-ranking
├── agents.py          # 4 CrewAI agent definitions
├── tasks.py           # 4 sequential task definitions
├── crew.py            # Crew assembly & execution
├── evaluate.py        # 25-query evaluation framework
├── main.py            # CLI entry point
├── requirements.txt   # Python dependencies
├── data/
│   ├── courses/       # 20 course description files
│   ├── programs/      # 2 program requirement files
│   ├── policies/      # 1 academic policy file
│   └── sources.md     # URL documentation
├── vectorstore/       # ChromaDB persistent storage
└── results/           # Evaluation output files
```

## Data Sources

All data sourced from Stanford University's public academic catalog:
- **Course Catalog:** https://explorecourses.stanford.edu/
- **Degree Programs:** https://exploredegrees.stanford.edu/
- **Academic Policies:** https://exploredegrees.stanford.edu/academicpoliciesandstatements/

See `data/sources.md` for full URL listing with access dates.

## Output Format

Every response follows the mandatory structure:
```
Answer / Plan: [Decision or Course List]
Why (requirements/prereqs satisfied): [Reasoning with citations]
Citations: [URLs with section names]
Clarifying questions (if needed): [Questions or N/A]
Assumptions / Not in catalog: [Assumptions or guidance]
```

## License

MIT
