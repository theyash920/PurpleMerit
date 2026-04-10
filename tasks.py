"""
CrewAI Task definitions — TOKEN-EFFICIENT PIPELINE.

Tasks accept a pre-built context string from the controller that includes:
  - Extracted memory state from previous turns
  - Truncated recent history (last 3 messages)
  - The current user query

3 task factories:
  1. Retrieval Task   — Catalog search (uses context for better queries)
  2. Planning Task    — Reasoning + verification + JSON output with memory
  3. FAQ Task         — Lightweight policy/general answers + JSON output with memory
"""
from crewai import Task
from agents import (
    retriever_agent,
    planner_agent,
    faq_agent,
    catalog_search_tool,
)


# ─── JSON Output Schema (shared) ────────────────────────────────────────────

JSON_EXPECTED_OUTPUT = (
    'You MUST return a raw JSON string (no markdown, no code fences). '
    'The JSON must have this structure:\n'
    '{\n'
    '  "answer": "Your full formatted answer with Answer/Plan, Why, Citations, Assumptions sections",\n'
    '  "memory": {\n'
    '    "last_topic": "brief description of what was discussed",\n'
    '    "courses_discussed": ["CS161"],\n'
    '    "query_type": "prerequisite_check",\n'
    '    "turn_count": 1\n'
    '  }\n'
    '}'
)


# ─── Task 1: Retrieval ──────────────────────────────────────────────────────

def create_retrieval_task(context_string: str) -> Task:
    """
    Create a retrieval task. The context_string already contains the
    current query, recent history, and memory state (built by controller).
    """
    return Task(
        description=(
            f"Search the Stanford catalog for documents needed to answer "
            f"the student's question.\n\n"
            f"{context_string}\n\n"
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

def create_planning_task(context_string: str, retrieval_task: Task) -> Task:
    """
    Create a planning task that uses retrieved docs and conversation context.
    Enforces JSON output with memory state.
    """
    return Task(
        description=(
            f"Using ONLY the retrieved catalog docs, answer the student's question.\n\n"
            f"{context_string}\n\n"
            f"Rules:\n"
            f"- Use only retrieved info. Cite URLs for every claim.\n"
            f"- If not in docs, say 'I don't have that information.'\n"
            f"- If conversation state is provided above, use it to maintain context "
            f"  (e.g. remember which courses the student has completed from prior turns).\n"
            f"- Update the memory state with any new information from this turn.\n\n"
            f"Your answer field should contain:\n"
            f"Answer / Plan: [Decision]\n"
            f"Why (requirements/prereqs satisfied): [Reasoning with URLs]\n"
            f"Citations:\n- [URL] - [Doc name]\n"
            f"Clarifying questions (if needed): [Questions or N/A]\n"
            f"Assumptions / Not in catalog: [Any gaps]"
        ),
        expected_output=JSON_EXPECTED_OUTPUT,
        agent=planner_agent,
        context=[retrieval_task],
    )


# ─── Task 3: FAQ ────────────────────────────────────────────────────────────

def create_faq_task(context_string: str) -> Task:
    """
    Create a lightweight FAQ task for policy/general questions.
    Uses the catalog search tool directly and returns JSON with memory.
    """
    return Task(
        description=(
            f"Answer the following general/policy question using the Stanford catalog.\n\n"
            f"{context_string}\n\n"
            f"Rules:\n"
            f"- Search the catalog if needed using the Catalog Search Tool.\n"
            f"- Be concise and direct.\n"
            f"- Cite source URLs for every claim.\n"
            f"- If not in the catalog, say so clearly.\n"
            f"- If conversation state is provided above, use it to maintain context.\n"
            f"- Update the memory state with any new information from this turn.\n\n"
            f"Your answer field should contain:\n"
            f"Answer: [Your response]\n"
            f"Citations:\n- [URL] - [Doc name]\n"
            f"Assumptions: [Any gaps or N/A]"
        ),
        expected_output=JSON_EXPECTED_OUTPUT,
        agent=faq_agent,
        tools=[catalog_search_tool],
    )
