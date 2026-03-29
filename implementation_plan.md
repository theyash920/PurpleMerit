# Agentic RAG Challenge Implementation Plan

This implementation plan is an exhaustive breakdown of the requirements for the "Prerequisite & Course Planning Assistant" project. Because the project directory is named `Agentic-RAG-using-Crew-AI`, this plan leans heavily into the **CrewAI** path, fulfilling all mandatory agentic requirements.

## User Review Required

> [!IMPORTANT]  
> Please review the architecture and agent design below. Since the project name mentions CrewAI, I have designed this around a 4-agent CrewAI system. 
> 
> Also, confirm that the Stanford dataset we just generated is acceptable to use as the base catalog for this challenge, as it fully meets the 20+ courses, 2+ programs, 1+ policy requirement.

---

## 1. Data Requirements (Completed)

We have already curated the dataset using Stanford University's public catalog:
*   **Courses:** 20 distinct course pages (e.g., CS106A, CS106B, CS111).
*   **Programs:** 2 programs (BS in CS, Minor in CS).
*   **Policies:** 1 academic policy (Grading).
*   **Documentation:** `sources.md` contains URLs, dates accessed (March 28, 2026), and brief descriptions.

---

## 2. RAG Pipeline Architecture

### Document Ingestion
*   Read the text files from the `data/` folder.
*   Extract the `SOURCE:` link and `COURSE/PROGRAM/POLICY` title from each file to use as **metadata**. 

### Cleaning & Chunking Strategy
*   **Strategy:** Because course descriptions are generally short (1-2 paragraphs), we will use **document-level chunking** for courses, or semantic chunking with a `RecursiveCharacterTextSplitter`.
*   **Chunk Size:** 500 characters.
*   **Overlap:** 50 characters (to ensure prerequisite logic isn't cut cleanly in half).
*   **Metadata:** *Crucially*, the source URL and Title must be injected into the metadata of *every single chunk*.

### Embeddings & Vector Store
*   **Embeddings Model:** OpenAI `text-embedding-3-small` (or equivalent open-source like `BAAI/bge-small-en-v1.5` depending on your API key availability).
*   **Vector Store:** ChromaDB (easy to run locally inside the notebook/app).
*   **Retriever Config:** `k=5` (Top 5 chunks) using Cosine Similarity.

---

## 3. Agentic Design (CrewAI)

We will implement a 4-Agent crew to handle the strict logic, reasoning, and formatting requirements.

### Agent 1: The Intake Agent (Input Parsing & Clarification)
*   **Role:** Student Profile Analyzer.
*   **Goal:** Determine if the user's prompt contains enough information to answer the question, or if clarification is needed.
*   **Task:** If asked to generate a *course plan*, it checks for completed courses, target major, and target term. 
*   **Behavior:** If missing, it immediately outputs 1-5 clarifying questions and halts the pipeline.

### Agent 2: The Catalog Retriever Agent (RAG Search)
*   **Role:** Catalog Researcher.
*   **Goal:** Search the Vector database strictly using the user's query and return exact text chunks with their associated URL metadata.
*   **Tools:** `ChromaDB_Search_Tool`.

### Agent 3: The Planner & Logic Agent (Reasoning)
*   **Role:** Academic Advisor.
*   **Goal:** Apply the rules retrieved by Agent 2 to the profile parsed by Agent 1.
*   **Capabilities:** 
    *   Prerequisite reasoning (Eligible/Not Eligible).
    *   Course plan generation respecting prerequisites and co-requisites.
    *   **Abstraction:** If Agent 2 returns no relevant context, Agent 3 MUST output: *"I don’t have that information in the provided catalog/policies."*

### Agent 4: The Verifier/Auditor Agent (Quality Control)
*   **Role:** Strict Compliance Auditor.
*   **Goal:** Ensure the final output perfectly matches the mandatory output format and that *every single claim* has a URL citation attached to it. It will rewrite the final output if citations are missing.

---

## 4. Output Formatting Rules

The prompt for the Verifier Agent will enforce that **every** final output conforms to this exact markdown format:

```markdown
Answer / Plan: [Decision or Suggested List]
Why (requirements/prereqs satisfied): [Reasoning based on text]
Citations: [Exact URL + heading/chunk id from metadata]
Clarifying questions (if needed): [1-5 questions, or N/A]
Assumptions / Not in catalog: [Assumptions made, or "I don't have that information..."]
```

---

## 5. Evaluation Strategy 

I will write a Python script to iterate through a test set of 25 queries.

### The 25 Query Dataset:
1.  **10 Prerequisite Checks:** (e.g., "Can I take CS161 if I only have CS106A?")
2.  **5 Multi-Hop Chain Questions:** (e.g., "What is the full path to take CS221?")
3.  **5 Program Requirement Questions:** (e.g., "What math is required for the BS in CS?")
4.  **5 Trick / Not-in-Docs Questions:** (e.g., "Who teaches CS106A?", "Can I waive CS106B?", "Are classes offered in the Summer?")

### Reporting Metrics Script:
The script will output:
*   Citation Coverage Rate (% of answers with a valid URL).
*   Abstention Accuracy (Did it successfully say "I don't know" to all 5 trick questions?).
*   Grading rubric logs.

---

## Open Questions

> [!WARNING]
> 1. **LLM Choice:** Are we using OpenAI (GPT-4o/GPT-3.5) for the CrewAI agents, or a local model (via Ollama) / Anthropic? I need to know which API keys you will be using.
> 2. **UI Requirement:** Requirement 3 mentions "Option Demo (Recommended) - Gradio/Streamlit". Would you like me to build a Streamlit UI `app.py`, or keep this entirely inside a Jupyter Notebook?
