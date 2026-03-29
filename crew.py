"""
Crew assembly and execution module.

Assembles the 4-agent crew and runs the full pipeline:
  Intake → Retrieval → Planning → Verification

Provides a single `run(question)` function for end-to-end execution.
"""
from crewai import Crew, Process

from agents import intake_agent, retriever_agent, planner_agent, verifier_agent
from tasks import (
    create_intake_task,
    create_retrieval_task,
    create_planning_task,
    create_verification_task,
)


def run(question: str, verbose: bool = True) -> str:
    """
    Run the full Agentic RAG pipeline for a student question.

    Args:
        question: The student's academic query.
        verbose: Whether to print agent reasoning to console.

    Returns:
        The final verified, citation-grounded response string.
    """
    # Create tasks for this specific question
    intake_task = create_intake_task(question)
    retrieval_task = create_retrieval_task(question, intake_task)
    planning_task = create_planning_task(question, retrieval_task)
    verification_task = create_verification_task(question, planning_task)

    # Assemble crew
    crew = Crew(
        agents=[intake_agent, retriever_agent, planner_agent, verifier_agent],
        tasks=[intake_task, retrieval_task, planning_task, verification_task],
        process=Process.sequential,
        verbose=verbose,
    )

    # Execute
    result = crew.kickoff()

    # CrewAI returns a CrewOutput; extract the raw string
    if hasattr(result, "raw"):
        return result.raw
    return str(result)


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
