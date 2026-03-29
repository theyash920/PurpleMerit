"""
Hybrid retrieval module with dynamic-k and LLM-based re-ranking.

Pipeline:
1. Classify query intent (course vs program vs policy vs general).
2. Fetch top-N candidates from ChromaDB using semantic search,
   optionally filtered by doc_type metadata.
3. Re-rank candidates using Groq LLM scoring for relevance.
4. Return top-k results with full metadata for citation.
"""
import os
import re
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

import config


# ─── Load Resources ─────────────────────────────────────────────────────────

_embedder = None
_collection = None
_groq_client = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(config.EMBEDDING_MODEL)
    return _embedder


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        _collection = client.get_collection(config.CHROMA_COLLECTION_NAME)
    return _collection


def _get_groq() -> Groq:
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=config.GROQ_API_KEY)
    return _groq_client


# ─── Query Intent Classification ────────────────────────────────────────────

# Simple keyword-based intent routing (fast, no LLM call needed)
COURSE_PATTERNS = re.compile(
    r"\b(CS\d{2,4}[A-Z]?|MATH\d+|ENGR\d+[A-Z]?|prerequisite|prereq|"
    r"co-?requisite|before\s+taking|can\s+i\s+take|enroll)\b",
    re.IGNORECASE,
)

PROGRAM_PATTERNS = re.compile(
    r"\b(major|minor|degree|program|requirement|core\s+course|elective|"
    r"track|specialization|units\s+required|total\s+units)\b",
    re.IGNORECASE,
)

POLICY_PATTERNS = re.compile(
    r"\b(grad(e|ing)|GPA|repeat|credit\s+limit|probation|transfer|"
    r"incomplete|CR/NC|letter\s+grade|honors|residency)\b",
    re.IGNORECASE,
)


def classify_query(query: str) -> str:
    """Classify query intent into: course, program, policy, or general."""
    course_score = len(COURSE_PATTERNS.findall(query))
    program_score = len(PROGRAM_PATTERNS.findall(query))
    policy_score = len(POLICY_PATTERNS.findall(query))

    if course_score >= program_score and course_score >= policy_score and course_score > 0:
        return "course"
    elif program_score >= policy_score and program_score > 0:
        return "program"
    elif policy_score > 0:
        return "policy"
    return "general"


# ─── Retrieval ───────────────────────────────────────────────────────────────

def retrieve(query: str, k: int | None = None, doc_type_filter: str | None = None) -> list[dict]:
    """
    Perform semantic search against ChromaDB with optional metadata filtering.
    Returns list of dicts with keys: text, title, source_url, section_name, doc_type, score.
    """
    collection = _get_collection()
    embedder = _get_embedder()

    # Determine k
    if k is None:
        intent = classify_query(query)
        if intent == "course":
            k = config.RETRIEVAL_K_COURSES
        elif intent in ("program", "policy"):
            k = config.RETRIEVAL_K_PROGRAMS
        else:
            k = config.RETRIEVAL_K_DEFAULT

    # Fetch more candidates for re-ranking
    n_candidates = max(k, config.RERANK_CANDIDATES)

    # Embed query
    query_embedding = embedder.encode([query], normalize_embeddings=True).tolist()

    # Build where filter
    where_filter = None
    if doc_type_filter:
        where_filter = {"doc_type": doc_type_filter}

    # Query ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_candidates,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Flatten results
    candidates = []
    for i in range(len(results["ids"][0])):
        candidates.append({
            "text": results["documents"][0][i],
            "score": 1 - results["distances"][0][i],  # cosine similarity
            **(results["metadatas"][0][i] if results["metadatas"][0][i] else {}),
        })

    return candidates[:k] if len(candidates) <= k else rerank(query, candidates, k)


# ─── LLM Re-ranking ─────────────────────────────────────────────────────────

def rerank(query: str, candidates: list[dict], k: int) -> list[dict]:
    """
    Re-rank candidates using Groq LLM scoring.
    Asks the LLM to score each candidate on a 1-10 relevance scale.
    Returns top-k by LLM score.
    """
    groq = _get_groq()

    # Build candidate summaries for the LLM
    candidate_summaries = []
    for i, c in enumerate(candidates):
        title = c.get("title", "Unknown")
        section = c.get("section_name", "")
        snippet = c["text"][:300]
        candidate_summaries.append(f"[{i}] Title: {title} | Section: {section}\n{snippet}")

    prompt = f"""You are a relevance scoring assistant. Given a student's question and a list of 
catalog document chunks, score each chunk on a scale of 1-10 for relevance to answering the question.

Question: {query}

Chunks:
{chr(10).join(candidate_summaries)}

Return ONLY a JSON array of objects with "index" and "score" keys, sorted by score descending.
Example: [{{"index": 2, "score": 9}}, {{"index": 0, "score": 7}}]
"""

    try:
        response = groq.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()

        # Parse the JSON array
        import json
        # Extract JSON from potential markdown code blocks
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())
            # Sort by score descending and pick top-k
            scores.sort(key=lambda x: x.get("score", 0), reverse=True)
            reranked = []
            for entry in scores[:k]:
                idx = entry["index"]
                if 0 <= idx < len(candidates):
                    candidates[idx]["rerank_score"] = entry["score"]
                    reranked.append(candidates[idx])
            if reranked:
                return reranked
    except Exception as e:
        print(f"[Retriever] Re-ranking failed ({e}), falling back to similarity order.")

    # Fallback: return top-k by original similarity
    return sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:k]


# ─── Convenience: Full Hybrid Retrieve ───────────────────────────────────────

def hybrid_retrieve(query: str) -> list[dict]:
    """
    Full hybrid retrieval pipeline:
    1. Classify intent
    2. Retrieve with metadata filter
    3. Re-rank
    Returns citation-ready results.
    """
    intent = classify_query(query)

    if intent == "course":
        # For course queries, search courses first, then add program context
        course_results = retrieve(query, k=config.RETRIEVAL_K_COURSES, doc_type_filter="course")
        program_results = retrieve(query, k=2, doc_type_filter="program")
        return course_results + program_results
    elif intent == "program":
        program_results = retrieve(query, k=config.RETRIEVAL_K_PROGRAMS, doc_type_filter="program")
        course_results = retrieve(query, k=2, doc_type_filter="course")
        return program_results + course_results
    elif intent == "policy":
        return retrieve(query, k=config.RETRIEVAL_K_PROGRAMS, doc_type_filter="policy")
    else:
        return retrieve(query, k=config.RETRIEVAL_K_DEFAULT)


# ─── CLI Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_queries = [
        "Can I take CS161 if I have only completed CS106A?",
        "What are the requirements for the CS minor?",
        "What is the minimum GPA needed to graduate?",
    ]
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        print(f"Intent: {classify_query(q)}")
        results = hybrid_retrieve(q)
        for r in results:
            print(f"  -> [{r.get('doc_type')}] {r.get('title', '?')[:50]} (score={r.get('score', 0):.3f})")
            print(f"     URL: {r.get('source_url', 'N/A')}")
