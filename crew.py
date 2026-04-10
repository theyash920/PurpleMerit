"""
Crew assembly — TOKEN-EFFICIENT PIPELINE.

Two modes:
  1. run()          — Original 2-agent pipeline (for backward compat / evaluate)
  2. run_pipeline() — New token-efficient pipeline with controller routing

The pipeline:
  Controller (memory + sliding window + classifier)
    → Route: course_planning → Retriever + Planner Crew
    → Route: faq            → FAQ Agent Crew
    → Route: clarify        → Direct response (no LLM call)

Includes inter-agent delay to spread token usage across time.
"""
import json
import time
import re

from crewai import Crew, Process

from agents import retriever_agent, planner_agent, faq_agent, clear_search_cache
from tasks import (
    create_retrieval_task,
    create_planning_task,
    create_faq_task,
)
from controller import (
    classify_intent,
    build_context_string,
    extract_latest_memory,
)

MAX_CREW_RETRIES = 3


# ─── JSON Response Parser ───────────────────────────────────────────────────

def parse_agent_response(raw: str) -> dict:
    """
    Parse the raw agent output into a dict with 'answer' and 'memory' keys.
    Handles various LLM output formats (raw JSON, markdown-wrapped, etc.).
    Falls back to treating the entire output as the answer if JSON parsing fails.
    """
    content = raw.strip()

    # Strip markdown code fences if present
    content = re.sub(r'^```(?:json)?\s*\n?', '', content)
    content = re.sub(r'\n?```\s*$', '', content)
    content = content.strip()

    # Try direct JSON parse
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "answer" in data:
            return data
    except (json.JSONDecodeError, TypeError):
        pass

    # Try to find JSON object in the text
    json_match = re.search(r'\{.*"answer"\s*:.*\}', content, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if isinstance(data, dict) and "answer" in data:
                return data
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback: wrap the raw text as the answer with empty memory
    return {
        "answer": raw,
        "memory": {}
    }


# ─── Course Planning Crew ────────────────────────────────────────────────────

def _run_course_planning_crew(context_string: str, verbose: bool = True) -> str:
    """Run the Retriever → Planner crew for course planning questions."""
    retrieval_task = create_retrieval_task(context_string)
    planning_task = create_planning_task(context_string, retrieval_task)

    crew = Crew(
        agents=[retriever_agent, planner_agent],
        tasks=[retrieval_task, planning_task],
        process=Process.sequential,
        verbose=verbose,
    )

    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


# ─── FAQ Crew ────────────────────────────────────────────────────────────────

def _run_faq_crew(context_string: str, verbose: bool = True) -> str:
    """Run the FAQ agent crew for policy/general questions."""
    faq_task = create_faq_task(context_string)

    crew = Crew(
        agents=[faq_agent],
        tasks=[faq_task],
        process=Process.sequential,
        verbose=verbose,
    )

    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


# ─── Main Pipeline Entry Point ───────────────────────────────────────────────

def run_pipeline(
    question: str,
    conversation_history: list[dict] = None,
    verbose: bool = True,
) -> dict:
    """
    Token-efficient pipeline entry point.

    Args:
        question: The current user message.
        conversation_history: Full list of {"role": ..., "content": ...} messages.
        verbose: Whether to print agent reasoning.

    Returns:
        dict with keys:
          - "answer": str   (the human-readable response)
          - "memory": dict  (state for next turn)
          - "route": str    (which route was taken)
          - "raw_json": str (full JSON string for storage)
    """
    if conversation_history is None:
        conversation_history = []

    # Clear the search cache for this new query
    clear_search_cache()
    # 1. Classify intent (lightweight LLM call, ~80 tokens)
    route = classify_intent(question)
    print(f"\n🔀 [Controller] Route: {route}")

    # 2. Handle clarify route — no crew needed
    if route == "clarify":
        memory = extract_latest_memory(conversation_history)
        memory["last_topic"] = "clarification_needed"
        result = {
            "answer": (
                "I'd be happy to help! Could you please provide more details? "
                "For example:\n"
                "- Which specific course(s) are you asking about?\n"
                "- What courses have you already completed?\n"
                "- Are you asking about prerequisites, program requirements, or policies?"
            ),
            "memory": memory,
        }
        return {
            "answer": result["answer"],
            "memory": result["memory"],
            "route": route,
            "raw_json": json.dumps(result),
        }

    # 3. Build compact context string (memory + sliding window + query)
    context_string = build_context_string(question, conversation_history)
    print(f"📋 [Controller] Context length: {len(context_string)} chars")

    # 4. Run the appropriate crew with retries
    last_error = None
    for attempt in range(MAX_CREW_RETRIES):
        try:
            if route == "course_planning":
                raw_output = _run_course_planning_crew(context_string, verbose)
            else:  # faq
                raw_output = _run_faq_crew(context_string, verbose)

            # 5. Parse the JSON response
            parsed = parse_agent_response(raw_output)

            # Increment turn count in memory
            memory = parsed.get("memory", {})
            prev_memory = extract_latest_memory(conversation_history)
            turn_count = prev_memory.get("turn_count", 0) + 1
            memory["turn_count"] = turn_count

            return {
                "answer": parsed.get("answer", raw_output),
                "memory": memory,
                "route": route,
                "raw_json": json.dumps(parsed),
            }

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_rate_limit = "rate_limit" in err_str or "429" in err_str or "too many" in err_str

            if is_rate_limit and attempt < MAX_CREW_RETRIES - 1:
                wait = (attempt + 1) * 30
                print(f"\n⏳ Rate-limited (attempt {attempt+1}/{MAX_CREW_RETRIES}), waiting {wait}s...\n")
                time.sleep(wait)
            else:
                raise

    raise last_error


# ─── Legacy Entry Point (backward compat for evaluate mode) ──────────────────

def run(question: str, verbose: bool = True) -> str:
    """
    Original 2-agent pipeline — kept for backward compatibility with evaluate.py.
    Does NOT use the controller / sliding window / memory system.
    """
    from tasks import create_retrieval_task, create_planning_task

    # Clear the search cache for this new query
    clear_search_cache()
    last_error = None
    for attempt in range(MAX_CREW_RETRIES):
        # Build a simple context string (no history, no memory)
        context_string = f"=== CURRENT QUERY ===\n{question}"

        retrieval_task = create_retrieval_task(context_string)
        planning_task = create_planning_task(context_string, retrieval_task)

        crew = Crew(
            agents=[retriever_agent, planner_agent],
            tasks=[retrieval_task, planning_task],
            process=Process.sequential,
            verbose=verbose,
        )

        try:
            result = crew.kickoff()
            raw = result.raw if hasattr(result, "raw") else str(result)

            # Try to extract just the answer from JSON
            parsed = parse_agent_response(raw)
            return parsed.get("answer", raw)

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_rate_limit = "rate_limit" in err_str or "429" in err_str or "too many" in err_str

            if is_rate_limit and attempt < MAX_CREW_RETRIES - 1:
                wait = (attempt + 1) * 30
                print(f"\n⏳ Rate-limited (attempt {attempt+1}/{MAX_CREW_RETRIES}), waiting {wait}s...\n")
                time.sleep(wait)
            else:
                raise

    raise last_error


# ─── CLI Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_q = "Can I take CS161 if I have completed CS106A and CS106B?"
    print(f"\n{'='*70}")
    print(f"Question: {test_q}")
    print(f"{'='*70}\n")

    # Test with pipeline
    result = run_pipeline(test_q)
    print(f"\n{'='*70}")
    print("FINAL ANSWER:")
    print(f"{'='*70}")
    print(result["answer"])
    print(f"\nRoute: {result['route']}")
    print(f"Memory: {json.dumps(result['memory'], indent=2)}")
