"""
CrewAI Task definitions for the Prerequisite & Course Planning Assistant.

4 sequential tasks forming the processing pipeline:
1. Intake Task      - Profile parsing & completeness check
2. Retrieval Task   - Hybrid catalog search
3. Planning Task    - Context-grounded reasoning with CoT
4. Verification Task - Citation audit & format enforcement
"""
from crewai import Task
from agents import (
    intake_agent,
    retriever_agent,
    planner_agent,
    verifier_agent,
    catalog_search_tool,
)


# ─── Task 1: Intake ─────────────────────────────────────────────────────────

def create_intake_task(question: str) -> Task:
    return Task(
        description=(
            f"Analyze the following student question and determine if enough information "
            f"is provided to answer it.\n\n"
            f"Student Question: {question}\n\n"
            f"Check for the following:\n"
            f"- Are specific course names/numbers mentioned?\n"
            f"- Are completed courses listed (if needed for the question)?\n"
            f"- Is the target major/minor specified (if asking about program requirements)?\n"
            f"- Is the target term specified (if asking for a course plan)?\n"
            f"- Are grades mentioned (if relevant to prerequisite minimum grade checks)?\n\n"
            f"If information is SUFFICIENT: Output a normalized student profile summary.\n"
            f"If information is MISSING: Output 1-5 specific clarifying questions.\n\n"
            f"Do NOT answer the actual academic question — only assess completeness."
        ),
        expected_output=(
            "Either:\n"
            "A) A normalized student profile with: query_type (prerequisite_check / "
            "course_plan / program_info / policy_question), mentioned_courses, "
            "completed_courses, target_course, target_program, target_term, and the "
            "original question.\n"
            "OR\n"
            "B) A list of 1-5 clarifying questions prefixed with 'CLARIFICATION NEEDED:'"
        ),
        agent=intake_agent,
    )


# ─── Task 2: Retrieval ──────────────────────────────────────────────────────

def create_retrieval_task(question: str, intake_task: Task) -> Task:
    return Task(
        description=(
            f"Using the student profile from the Intake Agent, search the Stanford "
            f"catalog for ALL relevant documents needed to answer the question.\n\n"
            f"Original Question: {question}\n\n"
            f"Instructions:\n"
            f"1. Use the Catalog Search Tool to search for the target course.\n"
            f"2. If the question involves prerequisites, ALSO search for each "
            f"   prerequisite course mentioned in the target course's document.\n"
            f"3. If the question involves program requirements, search for the "
            f"   relevant program document.\n"
            f"4. If the question involves academic policies (grading, repeats, etc.), "
            f"   search for the policy document.\n"
            f"5. Return ALL retrieved documents with their full text and source URLs.\n\n"
            f"IMPORTANT: If the Intake Agent output 'CLARIFICATION NEEDED', pass that "
            f"through as your output without searching."
        ),
        expected_output=(
            "A comprehensive set of catalog document excerpts with:\n"
            "- Full text of each relevant document\n"
            "- Source URL for each document\n"
            "- Document type (course/program/policy)\n"
            "- Section name\n"
            "OR the clarification questions from the Intake Agent."
        ),
        agent=retriever_agent,
        context=[intake_task],
        tools=[catalog_search_tool],
    )


# ─── Task 3: Planning ───────────────────────────────────────────────────────

def create_planning_task(question: str, retrieval_task: Task) -> Task:
    return Task(
        description=(
            f"Using ONLY the catalog documents retrieved by the Catalog Researcher, "
            f"answer the student's question.\n\n"
            f"Student Question: {question}\n\n"
            f"STRICT RULES:\n"
            f"1. Use ONLY the information from the retrieved documents. Do NOT use any "
            f"   prior knowledge about courses, universities, or academic policies.\n"
            f"2. For every claim, note the source URL from the retrieved document.\n"
            f"3. If the retrieved documents do not contain the answer, respond with: "
            f"   'I don't have that information in the provided catalog/policies.'\n"
            f"4. Include a <reasoning_trace> section showing your step-by-step logic.\n\n"
            f"For PREREQUISITE questions:\n"
            f"- List student's completed courses\n"
            f"- List target course prerequisites (from docs)\n"
            f"- Match each requirement\n"
            f"- Decision: Eligible / Not Eligible / Need More Info\n\n"
            f"For COURSE PLAN questions:\n"
            f"- List degree requirements (from docs)\n"
            f"- Filter out completed courses\n"
            f"- Select eligible courses within credit limit\n"
            f"- Include justification per course\n"
            f"- Include risks/assumptions section\n\n"
            f"If the Intake Agent requested clarification, pass those questions through."
        ),
        expected_output=(
            "A structured response containing:\n"
            "- Answer/Plan with decision or suggested courses\n"
            "- Reasoning with citations (source URLs)\n"
            "- <reasoning_trace> showing step-by-step logic\n"
            "- Any assumptions or information not in the catalog\n"
            "OR clarification questions from the Intake Agent."
        ),
        agent=planner_agent,
        context=[retrieval_task],
    )


# ─── Task 4: Verification ───────────────────────────────────────────────────

def create_verification_task(question: str, planning_task: Task) -> Task:
    return Task(
        description=(
            f"Audit the Planner's response for the following question:\n\n"
            f"Student Question: {question}\n\n"
            f"AUDIT CHECKLIST:\n"
            f"1. Does EVERY factual claim have a citation (URL)? If not, remove the claim "
            f"   or move it to 'Assumptions / Not in catalog'.\n"
            f"2. Are all cited URLs from the retrieved catalog documents (not invented)?\n"
            f"3. Does the output follow the EXACT mandatory format?\n"
            f"4. If the answer is 'I don't have that information', is guidance provided "
            f"   on what to check next?\n"
            f"5. Remove any <reasoning_trace> tags from the final output.\n\n"
            f"MANDATORY OUTPUT FORMAT (rewrite the response to match this exactly):\n\n"
            f"Answer / Plan: [Decision or Suggested Course List]\n\n"
            f"Why (requirements/prereqs satisfied): [Detailed reasoning with inline citations]\n\n"
            f"Citations:\n"
            f"- [URL 1] - [Section/Document name]\n"
            f"- [URL 2] - [Section/Document name]\n\n"
            f"Clarifying questions (if needed): [Questions or N/A]\n\n"
            f"Assumptions / Not in catalog: [Any assumptions or guidance]\n"
        ),
        expected_output=(
            "The final, audited response in the mandatory format with:\n"
            "- Answer / Plan\n"
            "- Why (requirements/prereqs satisfied) with citations\n"
            "- Citations list\n"
            "- Clarifying questions (if needed)\n"
            "- Assumptions / Not in catalog"
        ),
        agent=verifier_agent,
        context=[planning_task],
    )
