"""
Streamlit UI for the Prerequisite & Course Planning Assistant (Agentic RAG).

A polished web interface that wraps the CrewAI 4-agent pipeline:
  Intake → Retriever → Planner → Verifier

Run:
    streamlit run app.py
"""
import os
import sys
import time
import json
import streamlit as st
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

# ─── Page Configuration ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="Stanford Course Planning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hero Header ── */
    .hero-header {
        background: linear-gradient(135deg, #1a0533 0%, #2d1b4e 30%, #4a1942 60%, #8b1538 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(138, 21, 56, 0.25);
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
    }
    .hero-header h1 {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .hero-header p {
        color: rgba(255, 255, 255, 0.75);
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
    }

    /* ── Pipeline Badge ── */
    .pipeline-step {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 999px;
        padding: 6px 14px;
        margin: 4px;
        font-size: 0.78rem;
        font-weight: 500;
        color: rgba(255,255,255,0.88);
        transition: all 0.2s ease;
    }
    .pipeline-step:hover {
        background: rgba(255,255,255,0.14);
        transform: translateY(-1px);
    }
    .pipeline-arrow {
        color: rgba(255,255,255,0.3);
        font-size: 0.9rem;
        margin: 0 2px;
    }

    /* ── Chat Bubbles ── */
    .user-msg {
        background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.3rem;
        margin: 0.6rem 0;
        max-width: 75%;
        margin-left: auto;
        box-shadow: 0 4px 16px rgba(109, 40, 217, 0.25);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .assistant-msg {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 1.3rem 1.5rem;
        margin: 0.6rem 0;
        max-width: 85%;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        font-size: 0.93rem;
        line-height: 1.65;
    }

    /* ── Status Badges ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .status-ready {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .status-not-ready {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    .status-processing {
        background: rgba(99, 102, 241, 0.12);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }

    /* ── Sidebar Enhancements ── */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.6rem 0;
    }
    .sidebar-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: rgba(255,255,255,0.4);
        margin-bottom: 0.6rem;
    }

    /* ── Sample Question Cards ── */
    .sample-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin: 0.4rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.88rem;
        color: rgba(255,255,255,0.7);
    }
    .sample-card:hover {
        background: rgba(139, 92, 246, 0.08);
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateX(4px);
    }

    /* ── Metrics Cards ── */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.35);
        margin-top: 0.3rem;
    }

    /* ── Hide streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []          # UI display messages
if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = []  # Raw JSON history for memory extraction
if "vectorstore_ready" not in st.session_state:
    st.session_state.vectorstore_ready = os.path.exists(
        os.path.join(os.path.dirname(__file__), "vectorstore")
    )
if "eval_results" not in st.session_state:
    st.session_state.eval_results = None
if "last_route" not in st.session_state:
    st.session_state.last_route = None


# ─── Helper Functions ────────────────────────────────────────────────────────

def check_vectorstore() -> bool:
    """Check if the vectorstore directory exists and has data."""
    vs_dir = os.path.join(os.path.dirname(__file__), "vectorstore")
    return os.path.exists(vs_dir) and len(os.listdir(vs_dir)) > 0


def run_ingest():
    """Run the ingestion pipeline to build the vector store."""
    from ingest import load_documents, build_vectorstore
    chunks = load_documents()
    build_vectorstore(chunks)
    st.session_state.vectorstore_ready = True


def run_query(question: str) -> dict:
    """Run the token-efficient pipeline for a question."""
    from crew import run_pipeline
    return run_pipeline(
        question,
        conversation_history=st.session_state.pipeline_history,
        verbose=False,
    )


def format_response_sections(response: str) -> dict:
    """Try to parse the structured response into sections."""
    sections = {
        "answer": "",
        "reasoning": "",
        "citations": "",
        "clarifying": "",
        "assumptions": "",
    }

    # Try to parse the mandatory format
    markers = [
        ("Answer / Plan:", "answer"),
        ("Why (requirements/prereqs satisfied):", "reasoning"),
        ("Citations:", "citations"),
        ("Clarifying questions (if needed):", "clarifying"),
        ("Assumptions / Not in catalog:", "assumptions"),
    ]

    remaining = response
    for i, (marker, key) in enumerate(markers):
        if marker in remaining:
            idx = remaining.index(marker)
            # Find the next marker
            next_idx = len(remaining)
            for j in range(i + 1, len(markers)):
                if markers[j][0] in remaining:
                    next_idx = min(next_idx, remaining.index(markers[j][0]))

            sections[key] = remaining[idx + len(marker):next_idx].strip()
            remaining = remaining[next_idx:]

    # If no sections were parsed, return the raw response as the answer
    if not any(sections.values()):
        sections["answer"] = response

    return sections


# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 0.5rem 0;'>
        <div style='font-size: 2.5rem;'>🎓</div>
        <div style='font-size: 1.1rem; font-weight: 700; letter-spacing: -0.3px; margin-top: 0.3rem;'>
            Course Planner
        </div>
        <div style='font-size: 0.72rem; color: rgba(255,255,255,0.4); font-weight: 500; margin-top: 0.2rem;'>
            Agentic RAG • CrewAI
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── System Status ──
    st.markdown('<div class="sidebar-title">⚡ System Status</div>', unsafe_allow_html=True)

    vs_ready = check_vectorstore()
    if vs_ready:
        st.markdown(
            '<span class="status-badge status-ready">● Vector Store Ready</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-not-ready">○ Vector Store Not Built</span>',
            unsafe_allow_html=True,
        )

    st.markdown("", unsafe_allow_html=True)

    # ── Actions ──
    st.markdown('<div class="sidebar-title">🔧 Actions</div>', unsafe_allow_html=True)

    if st.button("📦 Build Vector Store", use_container_width=True, type="primary"):
        with st.spinner("Ingesting documents & building embeddings..."):
            try:
                run_ingest()
                st.success("✅ Vector store built successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Ingestion failed: {e}")

    if st.button("🧪 Run Evaluation (25 queries)", use_container_width=True):
        if not vs_ready:
            st.warning("⚠️ Build the vector store first!")
        else:
            with st.spinner("Running 25-query evaluation... This may take a few minutes."):
                try:
                    from evaluate import run_evaluation
                    results = run_evaluation()
                    st.session_state.eval_results = results
                    st.success("✅ Evaluation complete!")
                except Exception as e:
                    st.error(f"❌ Evaluation failed: {e}")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pipeline_history = []
        st.session_state.last_route = None
        st.rerun()

    st.markdown("---")

    # ── Architecture Info ──
    st.markdown('<div class="sidebar-title">🏛️ Architecture</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section" style="font-size: 0.82rem; line-height: 1.6;">
        <strong>LLM:</strong> Groq (Llama 3.3 70B)<br>
        <strong>Embeddings:</strong> BGE-base-en-v1.5<br>
        <strong>Vector Store:</strong> ChromaDB<br>
        <strong>Framework:</strong> CrewAI<br>
        <strong>Retrieval:</strong> Hybrid + LLM Rerank
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Data Info ──
    st.markdown('<div class="sidebar-title">📊 Data Coverage</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">20</div>
            <div class="metric-label">Courses</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2</div>
            <div class="metric-label">Programs</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1</div>
            <div class="metric-label">Policy</div>
        </div>
        """, unsafe_allow_html=True)


# ─── Main Content ────────────────────────────────────────────────────────────

# Hero Header
st.markdown("""
<div class="hero-header">
    <h1>🎓 Stanford Course Planning Assistant</h1>
    <p>Agentic RAG system with grounded reasoning, prerequisite analysis, and verifiable citations</p>
    <div style="margin-top: 1rem;">
        <span class="pipeline-step">🔀 Classify</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">📚 Retrieve</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">🧠 Plan & Verify</span>
    </div>
    <div style="margin-top: 0.5rem; font-size: 0.75rem; color: rgba(255,255,255,0.5);">
        Token-efficient: Sliding Window (last 3) + Memory State + Agent Routing
    </div>
</div>
""", unsafe_allow_html=True)

# ── Evaluation Results Tab ──
if st.session_state.eval_results:
    with st.expander("📊 Latest Evaluation Results", expanded=False):
        metrics = st.session_state.eval_results.get("metrics", {})
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Queries", metrics.get("total_queries", "—"))
        with cols[1]:
            st.metric("Citation Coverage", metrics.get("citation_coverage_rate", "—"))
        with cols[2]:
            st.metric("Abstention Accuracy", metrics.get("abstention_accuracy", "—"))
        with cols[3]:
            st.metric("Eligibility Correctness", metrics.get("eligibility_correctness", "—"))

# ── Check if ready ──
if not check_vectorstore():
    st.markdown("---")
    st.info(
        "👋 **Welcome!** To get started, click **📦 Build Vector Store** in the sidebar "
        "to ingest the Stanford catalog data. This only needs to be done once."
    )

# ── Sample Questions ──
if not st.session_state.messages:
    st.markdown("### 💡 Try asking...")

    sample_questions = [
        ("🔗 Prerequisite Check", "Can I take CS161 if I have completed CS106A and CS106B?"),
        ("🔄 Multi-hop Chain", "What is the full prerequisite chain to take CS221 starting from scratch?"),
        ("📋 Program Requirements", "What are the core requirements for the BS in Computer Science at Stanford?"),
        ("📜 Policy Question", "What is the minimum GPA requirement for the CS major?"),
        ("❓ Out-of-Scope Test", "Who teaches CS106A this quarter?"),
    ]

    cols = st.columns(2)
    for i, (label, question) in enumerate(sample_questions):
        with cols[i % 2]:
            if st.button(f"{label}", key=f"sample_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
            st.caption(question)

# ── Chat History ──
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        # Try to render structured response
        sections = format_response_sections(msg["content"])

        st.markdown('<div class="assistant-msg">', unsafe_allow_html=True)

        if "route" in msg:
            route_name = msg["route"]
            if route_name == "course_planning":
                display_text = "🤖 Agents: Retriever + Planner"
                color = "rgba(139, 92, 246, 0.3)" # Purple
                border = "rgba(139, 92, 246, 0.5)"
            elif route_name == "faq":
                display_text = "🤖 Agent: FAQ Advisor"
                color = "rgba(16, 185, 129, 0.2)" # Green
                border = "rgba(16, 185, 129, 0.4)"
            elif route_name == "clarify":
                display_text = "⚡ Router: Direct Clarification (0 Agents)"
                color = "rgba(245, 158, 11, 0.2)" # Orange
                border = "rgba(245, 158, 11, 0.4)"
            else:
                display_text = "🤖 Agent: Default"
                color = "rgba(255,255,255,0.1)"
                border = "rgba(255,255,255,0.2)"
            
            st.markdown(f'<div style="margin-bottom: 12px;"><span class="pipeline-step" style="background: {color}; border: 1px solid {border}; color: rgba(255,255,255,0.9); font-size: 0.7rem; padding: 4px 10px;">{display_text}</span></div>', unsafe_allow_html=True)

        if sections["answer"]:
            st.markdown(f"**📋 Answer / Plan**\n\n{sections['answer']}")

        if sections["reasoning"]:
            st.markdown(f"**💡 Why (reasoning)**\n\n{sections['reasoning']}")

        if sections["citations"]:
            st.markdown(f"**🔗 Citations**\n\n{sections['citations']}")

        if sections["clarifying"]:
            st.markdown(f"**❓ Clarifying Questions**\n\n{sections['clarifying']}")

        if sections["assumptions"]:
            st.markdown(f"**⚠️ Assumptions / Not in Catalog**\n\n{sections['assumptions']}")

        # Show timestamp if available
        if "timestamp" in msg:
            st.caption(f"🕐 {msg['timestamp']}")

        st.markdown('</div>', unsafe_allow_html=True)

# ── Process pending question ──
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]

    if not check_vectorstore():
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ The vector store has not been built yet. Please click **📦 Build Vector Store** in the sidebar first.",
            "timestamp": datetime.now().strftime("%I:%M %p"),
        })
        st.rerun()
    else:
        # Add user message to pipeline history
        st.session_state.pipeline_history.append({
            "role": "user",
            "content": last_msg["content"],
        })

        # Show processing indicator
        with st.status("🔄 Processing through token-efficient pipeline...", expanded=True) as status:
            st.write("🔀 **Step 1:** Classifying intent & extracting memory state...")
            time.sleep(0.3)

            try:
                result = run_query(last_msg["content"])
                route = result.get("route", "unknown")
                st.session_state.last_route = route

                if route == "course_planning":
                    st.write("📚 **Step 2:** Catalog Retriever — searching catalog...")
                    st.write("🧠 **Step 3:** Planner — reasoning & verifying citations...")
                elif route == "faq":
                    st.write("💡 **Step 2:** FAQ Agent — answering policy question...")
                else:
                    st.write("❓ **Step 2:** Requesting clarification...")

                response_text = result.get("answer", str(result))
                status.update(label=f"✅ Pipeline complete! (Route: {route})", state="complete")

                # Store raw JSON in pipeline history for memory extraction
                st.session_state.pipeline_history.append({
                    "role": "assistant",
                    "content": result.get("raw_json", json.dumps(result)),
                })

            except Exception as e:
                response_text = f"❌ An error occurred: {str(e)}\n\nPlease check your Groq API key and try again."
                status.update(label="❌ Pipeline failed", state="error")
                # Store error in pipeline history
                st.session_state.pipeline_history.append({
                    "role": "assistant",
                    "content": json.dumps({"answer": response_text, "memory": {}}),
                })

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "route": route,
            "timestamp": datetime.now().strftime("%I:%M %p"),
        })
        st.rerun()

# ── Chat Input ──
st.markdown("---")
user_input = st.chat_input("Ask about courses, prerequisites, program requirements, or policies...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()
