"""
Document ingestion module with structure-aware semantic chunking.

Strategy:
- Course files: kept as a SINGLE chunk each (they are short and contain tightly
  coupled prerequisite logic that must not be split).
- Program/Policy files: split on section headers (lines starting with uppercase
  keywords followed by a colon) so each logical section becomes a separate chunk
  while preserving context.

Every chunk carries rich metadata:
  title, source_url, section_name, doc_type, prerequisites (if course)
"""
import os
import re
import chromadb
from sentence_transformers import SentenceTransformer

import config


# ─── Metadata Extraction ────────────────────────────────────────────────────

def _parse_field(text: str, field: str) -> str:
    """Extract a field value from structured text like 'FIELD:\\nvalue'."""
    pattern = rf"^{field}:\s*\n?(.*?)(?=\n[A-Z_]+:|$)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: try single-line
    pattern2 = rf"^{field}:\s*(.+)"
    match2 = re.search(pattern2, text, re.MULTILINE)
    return match2.group(1).strip() if match2 else ""


def _extract_course_metadata(text: str) -> dict:
    """Extract rich metadata from a course file."""
    return {
        "doc_type": "course",
        "title": f"{_parse_field(text, 'COURSE')} - {_parse_field(text, 'TITLE')}",
        "course_id": _parse_field(text, "COURSE"),
        "prerequisites": _parse_field(text, "PREREQUISITES"),
        "prereq_logic": _parse_field(text, "PREREQ_LOGIC"),
        "corequisites": _parse_field(text, "CO-REQUISITES"),
        "min_grade": _parse_field(text, "MINIMUM_GRADE"),
        "units": _parse_field(text, "UNITS"),
        "source_url": _parse_field(text, "SOURCE"),
        "section_name": "Full Course Description",
    }


def _extract_program_metadata(text: str) -> dict:
    """Extract rich metadata from a program file."""
    return {
        "doc_type": "program",
        "title": _parse_field(text, "PROGRAM"),
        "source_url": _parse_field(text, "SOURCE"),
        "section_name": "Full Program Requirements",
    }


def _extract_policy_metadata(text: str) -> dict:
    """Extract rich metadata from a policy file."""
    return {
        "doc_type": "policy",
        "title": _parse_field(text, "POLICY"),
        "source_url": _parse_field(text, "SOURCE"),
        "section_name": "Full Policy Document",
    }


# ─── Section-Based Splitting ────────────────────────────────────────────────

# Patterns that indicate a new logical section in program/policy docs
SECTION_HEADERS = re.compile(
    r"^(REQUIREMENTS|DESCRIPTION|CORE REQUIREMENTS|ELECTIVE REQUIREMENTS|"
    r"GRADING SCALE|GRADE REQUIREMENTS|REPEATING COURSES|CREDIT LIMITS|"
    r"INCOMPLETES|ACADEMIC PROBATION|TRANSFER CREDITS|HONORS|"
    r"APPLICATION PROCESS|SENIOR PROJECT|TRACK ELECTIVES|"
    r"TOTAL UNITS|RESIDENCY REQUIREMENT|MINIMUM GPA|ACADEMIC STANDING|"
    r"OVERLAP POLICY|OFFERED):",
    re.MULTILINE
)


def _split_by_sections(text: str, base_metadata: dict) -> list[dict]:
    """
    Split a program or policy document into semantic chunks at section boundaries.
    Each chunk gets the base metadata plus the specific section name.
    """
    chunks = []
    positions = [(m.start(), m.group(1)) for m in SECTION_HEADERS.finditer(text)]

    if not positions:
        # No section headers found — treat as single chunk
        return [{"text": text.strip(), **base_metadata}]

    # Add header/preamble as first chunk
    preamble = text[: positions[0][0]].strip()
    if preamble:
        meta = {**base_metadata, "section_name": "Header / Overview"}
        chunks.append({"text": preamble, **meta})

    # Each section from header to the next header
    for i, (start, header) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        section_text = text[start:end].strip()
        if section_text:
            meta = {**base_metadata, "section_name": header}
            chunks.append({"text": section_text, **meta})

    return chunks


# ─── Main Ingestion Pipeline ────────────────────────────────────────────────

def load_documents() -> list[dict]:
    """
    Load all documents from the data directory.
    Returns a list of chunk dicts, each containing 'text' and metadata keys.
    """
    chunks = []

    # ── Courses: 1 chunk per course ──
    for fname in sorted(os.listdir(config.COURSES_DIR)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(config.COURSES_DIR, fname)
        with open(path) as f:
            text = f.read()
        meta = _extract_course_metadata(text)
        chunks.append({"text": text.strip(), **meta})

    # ── Programs: split by section ──
    for fname in sorted(os.listdir(config.PROGRAMS_DIR)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(config.PROGRAMS_DIR, fname)
        with open(path) as f:
            text = f.read()
        meta = _extract_program_metadata(text)
        section_chunks = _split_by_sections(text, meta)
        chunks.extend(section_chunks)

    # ── Policies: split by section ──
    for fname in sorted(os.listdir(config.POLICIES_DIR)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(config.POLICIES_DIR, fname)
        with open(path) as f:
            text = f.read()
        meta = _extract_policy_metadata(text)
        section_chunks = _split_by_sections(text, meta)
        chunks.extend(section_chunks)

    return chunks


def build_vectorstore(chunks: list[dict] | None = None) -> chromadb.Collection:
    """
    Embed all chunks and store them in ChromaDB.
    Returns the ChromaDB collection.
    """
    if chunks is None:
        chunks = load_documents()

    print(f"[Ingest] Loaded {len(chunks)} chunks from data directory.")

    # Initialize embedding model
    print(f"[Ingest] Loading embedding model: {config.EMBEDDING_MODEL}...")
    embedder = SentenceTransformer(config.EMBEDDING_MODEL)

    # Prepare texts and metadata
    texts = [c["text"] for c in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = []
    for c in chunks:
        meta = {k: v for k, v in c.items() if k != "text" and v}
        metadatas.append(meta)

    # Embed
    print("[Ingest] Generating embeddings...")
    embeddings = embedder.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    # Store in ChromaDB
    os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)

    # Delete collection if it exists (rebuild)
    try:
        client.delete_collection(config.CHROMA_COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print(f"[Ingest] Stored {len(chunks)} chunks in ChromaDB at {config.CHROMA_PERSIST_DIR}")
    return collection


# ─── CLI Entrypoint ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    chunks = load_documents()
    print(f"\n{'='*60}")
    print(f"Total chunks: {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"  [{i}] {c.get('doc_type','?'):8s} | {c.get('title','?')[:50]:50s} | section: {c.get('section_name','?')}")
    print(f"{'='*60}\n")
    build_vectorstore(chunks)
