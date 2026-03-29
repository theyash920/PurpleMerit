"""
Main CLI entry point for the Prerequisite & Course Planning Assistant.

Usage:
    python main.py ingest          # Build the vector store from data/
    python main.py ask "question"  # Ask a single question
    python main.py evaluate        # Run the 25-query evaluation set
    python main.py interactive     # Interactive chat mode
"""
import sys
import os

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
    """Ask a single question and print the answer."""
    from crew import run
    print(f"\n{'='*70}")
    print(f"Question: {question}")
    print(f"{'='*70}\n")
    answer = run(question)
    print(f"\n{'='*70}")
    print("FINAL ANSWER:")
    print(f"{'='*70}")
    print(answer)
    print()


def cmd_interactive():
    """Interactive chat mode — ask questions one at a time."""
    from crew import run
    print("\n" + "="*70)
    print("  Stanford Course Planning Assistant (Interactive Mode)")
    print("  Type 'quit' or 'exit' to stop.")
    print("="*70 + "\n")

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

        print("\n[Processing...]\n")
        answer = run(question, verbose=False)
        print(f"\nAssistant:\n{answer}\n")


def cmd_evaluate():
    """Run the 25-query evaluation set."""
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
