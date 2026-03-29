# Agentic RAG Challenge: Task Checklist

## Phase 1: Data Curation & Preparation
- [x] Create 20 enriched course text files with static Stanford URLs
- [x] Create 2 program requirement files with static URLs
- [x] Create 1 academic policy file with static URLs
- [x] Build `sources.md` tracking all URLs and access dates
- [x] Enrich data with prereq logic, co-requisites, min grades, offered terms
- [ ] ⚠️ Expand data to meet 30,000+ word count requirement (currently ~2,800 words)

## Phase 2: RAG Pipeline Infrastructure
- [x] Create `config.py` with all settings (Groq API, model names, paths)
- [x] Create `ingest.py` with structure-aware chunking (courses=single chunk, programs/policies=section split)
- [x] Inject rich metadata (title, source_url, section_name, doc_type) into every chunk
- [x] Set up ChromaDB vector store with `BAAI/bge-base-en-v1.5` embeddings (code written)
- [x] Create `retriever.py` with hybrid retrieval (dynamic k + metadata filtering)
- [x] Implement LLM-based re-ranking via Groq

## Phase 3: CrewAI Agentic Design
- [x] Create `agents.py` with 4 agents:
  - [x] Intake Agent (profile parsing + clarifying questions)
  - [x] Catalog Retriever Agent (hybrid search tool integration)
  - [x] Planner Agent (strict context-only reasoning + CoT trace)
  - [x] Verifier Agent (citation enforcement + output formatting)

## Phase 4: Task Workflows
- [x] Create `tasks.py` with 4 sequential tasks:
  - [x] Task 1: Parse student query context
  - [x] Task 2: Hybrid retrieve & rerank context
  - [x] Task 3: Synthesize plan with CoT reasoning
  - [x] Task 4: Audit citations & enforce output format
- [x] Create `crew.py` to assemble crew and run end-to-end

## Phase 5: Entry Point & Demo
- [x] Create `main.py` CLI entry point (ingest/ask/interactive/evaluate commands)
- [x] Wire up full pipeline: query → intake → retrieve → plan → verify → output

## Phase 6: Evaluation Framework
- [x] Create `evaluate.py` with 25 test queries:
  - [x] 10 prerequisite checks
  - [x] 5 multi-hop chain questions
  - [x] 5 program requirement questions
  - [x] 5 "not-in-docs" abstention questions
- [x] Log Citation Coverage Rate & Abstention Accuracy
- [x] Save 3 detailed example interaction transcripts

## Phase 7: Final Deliverables
- [x] Update `README.md` with setup/run instructions
- [x] (Optional) Build Streamlit UI `app.py`
- [x] Write 1-page summary (architecture, tradeoffs, evaluation) → `summary.txt`

---

## ⚠️ NOT YET EXECUTED (requires running)
- [ ] Install Python dependencies (`pip install -r requirements.txt`)
- [ ] Run `python main.py ingest` to build the vector store
- [ ] Run `python main.py ask "test question"` to validate end-to-end
- [ ] Run `python main.py evaluate` to generate evaluation results
- [ ] Fix any runtime bugs discovered during testing
