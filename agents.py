"""
CrewAI Agent definitions for the Prerequisite & Course Planning Assistant.

OPTIMIZED FOR TOKEN EFFICIENCY:
  - JSON output enforcement on final answering agents (Planner, FAQ)
  - Memory state object returned in every response
  - 3 Agents:
    1. Retriever Agent  - Searches catalog, returns relevant docs with URLs.
    2. Planner Agent    - Reasons over docs, answers with citations, returns JSON with memory.
    3. FAQ Agent        - Handles simple policy/general questions, returns JSON with memory.
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

# Higher token budget for worker agents that need to return full JSON answers
worker_llm = LLM(
    api_key=config.GROQ_API_KEY,
    model=f"groq/{config.LLM_MODEL}",
    temperature=config.LLM_TEMPERATURE,
    max_tokens=config.WORKER_MAX_TOKENS,
)


# ─── Custom Tools ────────────────────────────────────────────────────────────

# Cache to prevent duplicate searches within the same session
_search_cache: dict[str, str] = {}


def clear_search_cache():
    """Clear the search cache (call between user queries)."""
    _search_cache.clear()


@tool("Catalog Search Tool")
def catalog_search_tool(query: str) -> str:
    """Search the Stanford catalog for course info, prerequisites, and policies.
    Each unique query is searched only once; repeated queries return cached results."""
    # Return cached result if this exact query was already searched
    cache_key = query.strip().lower()
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    results = retriever_module.hybrid_retrieve(query)

    if not results:
        output = "No relevant documents found."
        _search_cache[cache_key] = output
        return output

    formatted = []
    for i, r in enumerate(results):
        title = r.get("title", "Unknown")
        url = r.get("source_url", "N/A")
        prereqs = r.get("prerequisites", "Not listed")
        # Increase limit since course prerequisites appear after descriptions
        text = r.get("text", "")[:1500] 

        formatted.append(
            f"[{i+1}] {title}\n"
            f"URL: {url}\n"
            f"PREREQUISITES: {prereqs}\n"
            f"CONTENT:\n{text}\n"
        )

    output = "\n".join(formatted)
    _search_cache[cache_key] = output
    return output


# ─── JSON Output Instructions (shared across answering agents) ───────────────

JSON_OUTPUT_INSTRUCTIONS = (
    "\n\nCRITICAL — OUTPUT FORMAT:\n"
    "You MUST return your response as a raw JSON string with NO markdown formatting, "
    "NO code fences, NO extra text. Just the raw JSON object.\n"
    "The JSON MUST have this exact structure:\n"
    '{\n'
    '  "answer": "Your full formatted answer text here (include Answer/Plan, Why, Citations, etc.)",\n'
    '  "memory": {\n'
    '    "last_topic": "brief topic description",\n'
    '    "courses_discussed": ["CS161", "CS106B"],\n'
    '    "completed_courses": ["CS106A"],\n'
    '    "target_course": "CS161",\n'
    '    "query_type": "prerequisite_check | course_plan | program_req | policy | general",\n'
    '    "eligibility_result": "eligible | not_eligible | unknown | N/A",\n'
    '    "turn_count": 1\n'
    '  }\n'
    '}\n'
    "Only include memory fields that are relevant. Omit fields that are N/A.\n"
    "The 'answer' field should contain the full human-readable response.\n"
    "The 'memory' field captures state for the NEXT turn of conversation.\n"
)


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
        "Always return source URLs for citation.\n\n"
        "IMPORTANT RULES:\n"
        "- Make AT MOST 3 tool calls total. Search only for distinct, necessary queries.\n"
        "- NEVER search the same course or topic twice.\n"
        "- Once you have the relevant docs, STOP searching and return your Final Answer immediately.\n"
        "- For a prerequisite question like 'Can I take CS161?', search: 1) CS161, "
        "2) the prerequisite course(s). That's it — do NOT repeat searches."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[catalog_search_tool],
    max_iter=4,
)


# ─── Agent 2: Planner + Verifier Agent ──────────────────────────────────────

planner_agent = Agent(
    role="Academic Advisor",
    goal=(
        "Using ONLY retrieved catalog docs, answer the student's question with citations. "
        "If docs don't have the answer, say: 'I don't have that information in the catalog.'"
    ),
    backstory=(
        "You are an academic advisor. You MUST use ONLY the provided catalog docs. NEVER guess or use outside knowledge.\n"
        "If the information is not explicitly stated in the retrieved documents, you MUST state 'I do not have this information in the catalog'.\n"
        "For prerequisites: list requirements, check against student's courses, state eligibility.\n"
        "For course plans: list requirements, filter completed, select eligible courses.\n"
        "Every claim needs a source URL.\n"
        "If conversation state is provided, use it to maintain context about the student's "
        "situation across turns without needing the full history."
        + JSON_OUTPUT_INSTRUCTIONS
    ),
    verbose=True,
    allow_delegation=False,
    llm=worker_llm,
    max_iter=3,
)


# ─── Agent 3: FAQ Agent ─────────────────────────────────────────────────────

faq_agent = Agent(
    role="Policy & FAQ Advisor",
    goal=(
        "Answer general academic policy questions, grading questions, and "
        "simple factual queries using the catalog. Be concise and direct."
    ),
    backstory=(
        "You are a helpful academic FAQ advisor. You answer general policy questions "
        "about GPA requirements, grading policies, transfer credits, academic standing, "
        "and other non-course-specific topics.\n"
        "Use ONLY the provided catalog information. If the answer is not in the docs, "
        "say so clearly.\n"
        "If conversation state is provided, use it to maintain context.\n\n"
        "IMPORTANT: Make AT MOST 2 tool calls. Never search the same thing twice."
        + JSON_OUTPUT_INSTRUCTIONS
    ),
    verbose=True,
    allow_delegation=False,
    llm=worker_llm,
    tools=[catalog_search_tool],
    max_iter=4,
)
