"""
CrewAI Agent definitions for the Prerequisite & Course Planning Assistant.

OPTIMIZED FOR 12K TPM (Groq Free Tier):
  2 Agents (down from 4) to halve LLM calls:
  1. Retriever Agent  - Searches catalog, returns relevant docs with URLs.
  2. Planner Agent    - Reasons over docs, answers with citations, self-verifies.
"""
from crewai import Agent, LLM
from crewai.tools import tool

import config
import retriever as retriever_module


# ─── LLM Setup ──────────────────────────────────────────────────────────────

llm = LLM(
    api_key=config.GROQ_API_KEY,
    model=f"groq/{config.LLM_MODEL}",
    temperature=config.LLM_TEMPERATURE,
    max_tokens=config.LLM_MAX_TOKENS,
)


# ─── Custom Tools ────────────────────────────────────────────────────────────

@tool("Catalog Search Tool")
def catalog_search_tool(query: str) -> str:
    """Search the Stanford catalog for course info, prerequisites, and policies."""
    results = retriever_module.hybrid_retrieve(query)

    if not results:
        return "No relevant documents found."

    formatted = []
    for i, r in enumerate(results):
        title = r.get("title", "Unknown")
        url = r.get("source_url", "N/A")
        text = r.get("text", "")[:300]  # Truncate to save tokens

        formatted.append(
            f"[{i+1}] {title}\n"
            f"URL: {url}\n"
            f"{text}\n"
        )

    return "\n".join(formatted)


# ─── Agent 1: Catalog Retriever Agent ───────────────────────────────────────

retriever_agent = Agent(
    role="Catalog Researcher",
    goal=(
        "Search the Stanford catalog to find relevant course descriptions, "
        "prerequisites, and policies for the student's question. "
        "Return exact text and source URLs."
    ),
    backstory=(
        "You search the Stanford catalog database. "
        "For prerequisite questions, retrieve BOTH the target course AND its prerequisites. "
        "Always return source URLs for citation."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[catalog_search_tool],
)


# ─── Agent 2: Planner + Verifier Agent ──────────────────────────────────────

planner_agent = Agent(
    role="Academic Advisor",
    goal=(
        "Using ONLY retrieved catalog docs, answer the student's question with citations. "
        "If docs don't have the answer, say: 'I don't have that information in the catalog.'"
    ),
    backstory=(
        "You are an academic advisor. Use ONLY the provided catalog docs. Never guess.\n"
        "For prerequisites: list requirements, check against student's courses, state eligibility.\n"
        "For course plans: list requirements, filter completed, select eligible courses.\n"
        "Every claim needs a source URL. Format your response as:\n"
        "Answer / Plan: [Decision]\n"
        "Why: [Reasoning with URLs]\n"
        "Citations: [URL list]\n"
        "Assumptions: [Any gaps]"
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
)
