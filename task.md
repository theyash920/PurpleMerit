# Agentic RAG Challenge: Implementation Checklist

- `[x]` **Phase 1: Data Curation & Preparation**
  - `[x]` Scrape/create 20 course text files with static Stanford URLs.
  - `[x]` Scrape/create 2 program requirement files with static URLs.
  - `[x]` Scrape/create 1 academic policy file with static URLs.
  - `[x]` Update `sources.md` tracking all URLs and access dates.

- `[ ]` **Phase 2: RAG Pipeline Infrastructure**
  - `[ ]` Configure OpenAI Embeddings model (`text-embedding-3-small`).
  - `[ ]` Initialize ChromaDB vector store.
  - `[ ]` Implement semantic chunking logic (500 char chunk size, 50 char overlap).
  - `[ ]` Inject the exact `SOURCE:` URL into every chunk's metadata during ingestion.
  - `[ ]` Test index retrieval (Top K=5) with Cosine Similarity.

- `[ ]` **Phase 3: CrewAI Agentic Design**
  - `[ ]` **Intake Agent:** Create agent prompt to identify missing profile details (major, grades, term). Identify when to ask clarifying questions.
  - `[ ]` **Catalog Retriever Agent:** Implement ChromaDB Search tool integration so this agent can query the index.
  - `[ ]` **Planner Agent:** Create prompt rules for prerequisite logic, enforcing "I don't have that information" for missing policy answers.
  - `[ ]` **Verifier Agent:** Enforce strict Markdown output validation (Answer/Plan, Why, Citations, Questions, Assumptions).

- `[ ]` **Phase 4: Agent Tasks & Workflows**
  - `[ ]` Define Task 1: "Parse student query context".
  - `[ ]` Define Task 2: "Retrieve contextual catalog data".
  - `[ ]` Define Task 3: "Synthesize plan based on documents".
  - `[ ]` Define Task 4: "Audit generated plan against required formatting and cite sources".
  - `[ ]` Assemble Crew workflow (Sequential processing).

- `[ ]` **Phase 5: Evaluation Framework**
  - `[ ]` Create Python auto-grader script `evaluate.py`.
  - `[ ]` Build Test Set: 10 prerequisite short checks.
  - `[ ]` Build Test Set: 5 multi-hop chain checking cases.
  - `[ ]` Build Test Set: 5 program-level cases (Math requirements for BS).
  - `[ ]` Build Test Set: 5 "trick" questions (Not in catalog, forcing abstention).
  - `[ ]` Run evaluation and aggregate Citation Coverage Rate & Abstention Accuracy.
  - `[ ]` Save 3 specific example interaction transcripts.

- `[ ]` **Phase 6: Final Deliverables**
  - `[ ]` (Optional) Build Streamlit/Gradio UI `app.py` for end-to-end user interaction.
  - `[ ]` Write exactly 1-page PDF/Markdown summary on retrieval choices, agent roles, and evaluation failure modes.
  - `[ ]` Update `README.md` with setup and running instructions for GitHub submission.
