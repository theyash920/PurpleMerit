"""
CrewAI Task definitions — OPTIMIZED FOR 12K TPM.

2 sequential tasks (down from 4):
1. Retrieval Task   - Catalog search
2. Planning Task    - Reasoning + verification (combined)
"""
from crewai import Task
from agents import (
    retriever_agent,
    planner_agent,
    catalog_search_tool,
)


# ─── Task 1: Retrieval ──────────────────────────────────────────────────────

def create_retrieval_task(question: str) -> Task:
    return Task(
        description=(
            f"Search the Stanford catalog for documents needed to answer:\n\n"
            f"{question}\n\n"
            f"Use the Catalog Search Tool. For prerequisite questions, also search "
            f"for each prerequisite course. Return all docs with URLs.\n"
            f"Keep your response concise — just the retrieved facts and URLs."
        ),
        expected_output=(
            "Catalog excerpts with source URLs, document type, and key facts."
        ),
        agent=retriever_agent,
        tools=[catalog_search_tool],
    )


# ─── Task 2: Planning + Verification ────────────────────────────────────────

def create_planning_task(question: str, retrieval_task: Task) -> Task:
    return Task(
        description=(
            f"Using ONLY the retrieved catalog docs, answer:\n\n"
            f"{question}\n\n"
            f"Rules: Use only retrieved info. Cite URLs for every claim. "
            f"If not in docs, say 'I don't have that information.'\n\n"
            f"Format:\n"
            f"Answer / Plan: [Decision]\n"
            f"Why (requirements/prereqs satisfied): [Reasoning with URLs]\n"
            f"Citations:\n- [URL] - [Doc name]\n"
            f"Clarifying questions (if needed): [Questions or N/A]\n"
            f"Assumptions / Not in catalog: [Any gaps]"
        ),
        expected_output=(
            "Formatted response with Answer, Why, Citations, and Assumptions."
        ),
        agent=planner_agent,
        context=[retrieval_task],
    )
