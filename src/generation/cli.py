"""
Command-line interface for Cochrane Medical RAG system.
"""

import argparse
import sys

from src.generation.medical_rag_system import CochraneMedicalRAG


def handle_ask(rag: CochraneMedicalRAG, question: str):
    """Handle ask command."""
    try:
        result = rag.ask(question, format="string")
        print("\n" + result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def handle_search(rag: CochraneMedicalRAG, query: str, limit: int = 5):
    """Handle search command."""
    try:
        results = rag.search(query, top_k=limit)
        print(f"\nFound {len(results)} results\n")

        for idx, result in enumerate(results, 1):
            print(f"[{idx}] {result['title']}")
            if result["quality_grade"]:
                print(f"    Quality: Grade {result['quality_grade']}")
            if result["section"]:
                print(f"    Section: {result['section']}")
            print(f"    {result['content'][:200]}...\n")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def handle_stats(rag: CochraneMedicalRAG):
    """Handle stats command."""
    try:
        stats = rag.get_stats()
        print("\n=== SYSTEM STATISTICS ===")
        print(f"Total Chunks: {stats['total_chunks']:,}")
        print(f"Total Documents: {stats['total_documents']:,}")
        print(f"Model: {stats['model']}")
        print(f"Reranker: {'Enabled' if stats['reranker_enabled'] else 'Disabled'}")

        if stats.get("chunks_by_level"):
            print("\nChunks by Level:")
            for level, count in stats["chunks_by_level"].items():
                print(f"  {level}: {count:,}")
        print("")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def interactive_mode():
    """Run interactive CLI session."""
    print("Cochrane Medical RAG - Interactive Mode")
    print("Type '/help' for commands or '/quit' to exit\n")

    rag = CochraneMedicalRAG(verbose=True)

    try:
        while True:
            try:
                user_input = input("> ").strip()

                if not user_input:
                    continue

                if user_input == "/quit":
                    print("Goodbye!")
                    break
                elif user_input == "/help":
                    print("\nCommands:")
                    print("  /help              Show this help")
                    print("  /stats             Show system statistics")
                    print("  /search <query>    Search without LLM")
                    print("  /quit              Exit system")
                    print("\nJust type a question to get an answer!\n")
                elif user_input.startswith("/stats"):
                    handle_stats(rag)
                elif user_input.startswith("/search"):
                    parts = user_input.split(" ", 1)
                    if len(parts) < 2:
                        print("Usage: /search <query>")
                        continue
                    handle_search(rag, parts[1])
                else:
                    handle_ask(rag, user_input)
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type '/quit' to exit.")
            except EOFError:
                print("\n\nGoodbye!")
                break

    finally:
        rag.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Cochrane Medical RAG System")
    parser.add_argument(
        "--question", "-q", type=str, help="Ask a medical question"
    )
    parser.add_argument(
        "--search", "-s", type=str, help="Search for documents (no LLM)"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show system statistics"
    )
    parser.add_argument(
        "--model", type=str, help="OpenAI model to use"
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="Number of results (search mode)"
    )

    args = parser.parse_args()

    if args.question or args.search or args.stats:
        verbose = False
    else:
        verbose = True

    rag = CochraneMedicalRAG(model=args.model, verbose=verbose)

    try:
        if args.question:
            handle_ask(rag, args.question)
        elif args.search:
            handle_search(rag, args.search, limit=args.limit)
        elif args.stats:
            handle_stats(rag)
        else:
            interactive_mode()
    finally:
        rag.close()


if __name__ == "__main__":
    main()

