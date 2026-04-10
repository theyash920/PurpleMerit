"""
Main CLI entry point for the Prerequisite & Course Planning Assistant.

Usage:
    python main.py ingest          # Build the vector store from data/
    python main.py ask "question"  # Ask a single question (uses token-efficient pipeline)
    python main.py evaluate        # Run the 25-query evaluation set (legacy pipeline)
    python main.py interactive     # Interactive chat mode (with memory & sliding window)
"""
import sys
import os
import json

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))


def cmd_ingest():
    """Build the vector store from the data directory."""
    from ingest import load_documents, build_vectorstore
    print("\n[Main] Building vector store from data/...")
    chunks = load_documents()
    build_vectorstore(chunks)
    print("[Main] Done! Vector store is ready.\n")


def cmd_ask(question: str):
    """Ask a single question using the token-efficient pipeline."""
    from crew import run_pipeline
    print(f"\n{'='*70}")
    print(f"Question: {question}")
    print(f"{'='*70}\n")

    result = run_pipeline(question, conversation_history=[], verbose=True)

    print(f"\n{'='*70}")
    print(f"FINAL ANSWER (Route: {result['route']}):")
    print(f"{'='*70}")
    print(result["answer"])

    if result.get("memory"):
        print(f"\n📝 Memory State: {json.dumps(result['memory'], indent=2)}")
    print()


def cmd_interactive():
    """
    Interactive chat mode with full memory & sliding window support.
    Conversation history is maintained across turns.
    """
    from crew import run_pipeline
    print("\n" + "="*70)
    print("  Stanford Course Planning Assistant (Interactive Mode)")
    print("  Token-Efficient Pipeline — Sliding Window + Memory State")
    print("  Type 'quit' or 'exit' to stop.")
    print("  Type 'memory' to view current memory state.")
    print("  Type 'history' to view conversation history.")
    print("="*70 + "\n")

    conversation_history = []

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not question:
            continue

        # Debug commands
        if question.lower() == "memory":
            from controller import extract_latest_memory
            mem = extract_latest_memory(conversation_history)
            print(f"\n📝 Current Memory: {json.dumps(mem, indent=2)}\n")
            continue

        if question.lower() == "history":
            print(f"\n📜 History ({len(conversation_history)} messages):")
            for i, msg in enumerate(conversation_history):
                role = msg["role"].upper()
                content = msg["content"][:100]
                print(f"  [{i}] {role}: {content}...")
            print()
            continue

        # Add user message to history
        conversation_history.append({"role": "user", "content": question})

        print("\n[Processing...]\n")
        try:
            result = run_pipeline(
                question,
                conversation_history=conversation_history,
                verbose=False,
            )

            # Store the raw JSON as the assistant message (so memory can be extracted)
            conversation_history.append({
                "role": "assistant",
                "content": result["raw_json"],
            })

            # Display the human-readable answer
            print(f"\n🔀 Route: {result['route']}")
            print(f"\nAssistant:\n{result['answer']}\n")

            if result.get("memory"):
                print(f"📝 Memory: {json.dumps(result['memory'], indent=2)}\n")

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"\n{error_msg}\n")
            conversation_history.append({
                "role": "assistant",
                "content": json.dumps({"answer": error_msg, "memory": {}}),
            })


def cmd_evaluate():
    """Run the 25-query evaluation set (uses legacy pipeline for consistency)."""
    from evaluate import run_evaluation
    run_evaluation()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "ingest":
        cmd_ingest()
    elif command == "ask":
        if len(sys.argv) < 3:
            print("Usage: python main.py ask \"your question here\"")
            sys.exit(1)
        cmd_ask(" ".join(sys.argv[2:]))
    elif command == "interactive":
        cmd_interactive()
    elif command == "evaluate":
        cmd_evaluate()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
