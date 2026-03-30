"""
Crew assembly — OPTIMIZED FOR 12K TPM.

2-agent pipeline:
  Retriever → Planner/Verifier

Includes inter-agent delay to spread token usage across time.
"""
import time

from crewai import Crew, Process

from agents import retriever_agent, planner_agent
from tasks import (
    create_retrieval_task,
    create_planning_task,
)

MAX_CREW_RETRIES = 3


def run(question: str, verbose: bool = True) -> str:
    """
    Run the 2-agent Agentic RAG pipeline for a student question.

    Args:
        question: The student's academic query.
        verbose: Whether to print agent reasoning to console.

    Returns:
        The final citation-grounded response string.
    """
    last_error = None

    for attempt in range(MAX_CREW_RETRIES):
        # Create fresh tasks for each attempt
        retrieval_task = create_retrieval_task(question)
        planning_task = create_planning_task(question, retrieval_task)

        # Assemble 2-agent crew
        crew = Crew(
            agents=[retriever_agent, planner_agent],
            tasks=[retrieval_task, planning_task],
            process=Process.sequential,
            verbose=verbose,
        )

        try:
            result = crew.kickoff()

            if hasattr(result, "raw"):
                return result.raw
            return str(result)

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_rate_limit = "rate_limit" in err_str or "429" in err_str or "too many" in err_str

            if is_rate_limit and attempt < MAX_CREW_RETRIES - 1:
                wait = (attempt + 1) * 30  # 30s, 60s — longer waits for TPM reset
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
    answer = run(test_q)
    print(f"\n{'='*70}")
    print("FINAL ANSWER:")
    print(f"{'='*70}")
    print(answer)
