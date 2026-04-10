"""
Controller module — Token-efficient state management wrapper for CrewAI.

Implements:
  1. Sliding Window History — Only last N messages passed to agents.
  2. Memory Extraction    — Scans backward for the latest JSON "memory" dict.
  3. Guard/Classifier     — Lightweight intent routing before crew kick-off.
  4. Context Builder      — Constructs a compact context string for CrewAI tasks.
"""
import json
import re

from groq import Groq
import config


# ─── Memory Extraction ──────────────────────────────────────────────────────

def extract_latest_memory(messages: list[dict]) -> dict:
    """
    Iterate backward through message history.  Find the most recent
    assistant message that contains a JSON "memory" dictionary.
    Return the memory dict, or an empty dict if none found.
    """
    for msg in reversed(messages):
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", "")
        # Try to parse the whole content as JSON first
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "memory" in data:
                return data["memory"]
        except (json.JSONDecodeError, TypeError):
            pass
        # Try to find a JSON block embedded in the text
        json_match = re.search(r'\{[^{}]*"memory"\s*:\s*\{[^}]*\}[^}]*\}', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if "memory" in data:
                    return data["memory"]
            except (json.JSONDecodeError, TypeError):
                pass
    return {}


# ─── Sliding Window ─────────────────────────────────────────────────────────

def truncate_history(messages: list[dict], window: int = None) -> list[dict]:
    """
    Return only the last `window` messages from the conversation history.
    """
    if window is None:
        window = config.SLIDING_WINDOW_SIZE
    return messages[-window:] if len(messages) > window else list(messages)


def format_history_string(messages: list[dict]) -> str:
    """
    Convert a list of message dicts into a compact prompt-friendly string.
    Strips any embedded JSON/memory blocks from assistant messages for brevity.
    """
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        # For assistant messages, try to show only the "answer" part
        if role == "Assistant":
            try:
                data = json.loads(content)
                if isinstance(data, dict) and "answer" in data:
                    content = data["answer"]
            except (json.JSONDecodeError, TypeError):
                pass
        # Truncate long messages to save tokens
        if len(content) > 400:
            content = content[:400] + "..."
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


# ─── Guard / Classifier ─────────────────────────────────────────────────────

def classify_intent(user_message: str) -> str:
    """
    Lightweight intent classifier using a direct Groq API call.
    Returns one of: "course_planning", "faq", "clarify".

    This is intentionally cheap — uses minimal tokens.
    """
    groq = Groq(api_key=config.GROQ_API_KEY)

    system_prompt = (
        "You are a query classifier for a Stanford course planning assistant. "
        "Given a student's message, classify it into exactly ONE category.\n\n"
        "Categories:\n"
        "- course_planning: Questions about prerequisites, eligibility, course plans, "
        "specific courses (CS161, MATH51, etc.), degree requirements, program requirements.\n"
        "- faq: General policy questions (GPA, grading, transfer credits, academic standing), "
        "simple factual questions, or general help.\n"
        "- clarify: The message is unclear, too vague, or needs more information.\n\n"
        "Respond with ONLY the category name. Nothing else."
    )

    try:
        response = groq.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
            max_tokens=config.CLASSIFIER_MAX_TOKENS,
        )
        result = response.choices[0].message.content.strip().lower()

        # Normalize the response
        if "course" in result or "plan" in result or "prerequisite" in result:
            return "course_planning"
        elif "clarif" in result:
            return "clarify"
        else:
            return "faq"
    except Exception as e:
        print(f"[Controller] Classifier failed ({e}), defaulting to course_planning")
        return "course_planning"


# ─── Context Builder ─────────────────────────────────────────────────────────

def build_context_string(
    user_message: str,
    messages: list[dict],
) -> str:
    """
    Build the compact context string that gets injected into CrewAI task
    descriptions.  Combines:
      - Extracted memory state (from full history)
      - Truncated recent history (last N messages)
      - The current user query
    """
    # 1. Extract memory from FULL history (before truncation)
    memory = extract_latest_memory(messages)

    # 2. Truncate history to sliding window
    recent = truncate_history(messages)
    history_str = format_history_string(recent)

    # 3. Assemble
    parts = []

    if memory:
        parts.append(
            f"=== CONVERSATION STATE (from previous turns) ===\n"
            f"{json.dumps(memory, indent=2)}\n"
        )

    if history_str:
        parts.append(
            f"=== RECENT CONVERSATION (last {len(recent)} messages) ===\n"
            f"{history_str}\n"
        )

    parts.append(
        f"=== CURRENT QUERY ===\n"
        f"{user_message}"
    )

    return "\n".join(parts)
