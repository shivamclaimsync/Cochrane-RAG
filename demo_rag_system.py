"""
Demonstration script for Cochrane Medical RAG System.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.generation.medical_rag_system import CochraneMedicalRAG


def demo_1_simple_question():
    """Demo 1: Simple medical question."""
    print("\n" + "=" * 80)
    print("DEMO 1: Simple Medical Question")
    print("=" * 80)

    rag = CochraneMedicalRAG(verbose=False)

    question = "What is the effectiveness of vitamin C for preventing colds?"

    result = rag.ask(question, format="string")
    print(result)

    rag.close()


def demo_2_statistical_evidence():
    """Demo 2: Statistical evidence query."""
    print("\n" + "=" * 80)
    print("DEMO 2: Statistical Evidence Query")
    print("=" * 80)

    rag = CochraneMedicalRAG(verbose=False)

    question = (
        "What is the statistical evidence for aspirin "
        "in cardiovascular disease prevention?"
    )

    result = rag.ask(question, format="dict")

    print(f"\nAnswer:\n{result['answer']}\n")
    print(f"Statistical Summary: {result['statistical_summary']}")
    print(f"Quality Summary: {result['quality_summary']}")
    print(f"Sources Used: {result['num_sources']}")

    rag.close()


def demo_3_search_only():
    """Demo 3: Search-only mode."""
    print("\n" + "=" * 80)
    print("DEMO 3: Search-Only Mode (No LLM)")
    print("=" * 80)

    rag = CochraneMedicalRAG(verbose=False)

    query = "corticosteroids asthma"

    results = rag.search(query, top_k=3)

    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result['title']}")
        print(f"    Topic: {result['topic']}")
        if result["quality_grade"]:
            print(f"    Quality: Grade {result['quality_grade']}")
        if result["section"]:
            print(f"    Section: {result['section']}")
        print(f"    {result['content'][:150]}...")

    rag.close()


def demo_4_high_quality_filter():
    """Demo 4: High-quality filter."""
    print("\n" + "=" * 80)
    print("DEMO 4: High-Quality Filter (Grade A Only)")
    print("=" * 80)

    rag = CochraneMedicalRAG(verbose=False)

    question = "What are the effects of antibiotics for bacterial infections?"

    results = rag.search(query=question, filters={"quality_grade": "A"}, top_k=5)

    print(f"\nFound {len(results)} Grade A reviews:\n")

    for idx, result in enumerate(results, 1):
        print(f"[{idx}] {result['title']}")
        print(f"    Quality: Grade {result['quality_grade']}")

    rag.close()


def demo_5_section_search():
    """Demo 5: Section-specific search."""
    print("\n" + "=" * 80)
    print("DEMO 5: Section-Specific Search (Authors' Conclusions)")
    print("=" * 80)

    rag = CochraneMedicalRAG(verbose=False)

    question = "What are the clinical recommendations for diabetes management?"

    results = rag.search(
        query=question, filters={"section": "authors_conclusions"}, top_k=3
    )

    print(f"\nFound {len(results)} results from Authors' Conclusions:\n")

    for idx, result in enumerate(results, 1):
        print(f"[{idx}] {result['title']}")
        print(f"    Section: {result['section']}")
        print(f"    {result['content'][:150]}...\n")

    rag.close()


def demo_stats():
    """Display system statistics."""
    print("\n" + "=" * 80)
    print("SYSTEM STATISTICS")
    print("=" * 80)

    rag = CochraneMedicalRAG(verbose=False)

    stats = rag.get_stats()

    print(f"\nTotal Chunks: {stats['total_chunks']:,}")
    print(f"Total Documents: {stats['total_documents']:,}")
    print(f"Model: {stats['model']}")
    print(f"Reranker: {'Enabled' if stats['reranker_enabled'] else 'Disabled'}")

    if stats.get("chunks_by_level"):
        print("\nChunks by Level:")
        for level, count in stats["chunks_by_level"].items():
            print(f"  {level}: {count:,}")

    rag.close()


def main():
    """Run selected demo or all demos."""
    if len(sys.argv) > 1:
        demo_num = sys.argv[1]
        demo_map = {
            "1": demo_1_simple_question,
            "2": demo_2_statistical_evidence,
            "3": demo_3_search_only,
            "4": demo_4_high_quality_filter,
            "5": demo_5_section_search,
            "stats": demo_stats,
        }

        if demo_num in demo_map:
            try:
                demo_map[demo_num]()
            except Exception as e:
                print(f"\nError running demo: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Unknown demo: {demo_num}", file=sys.stderr)
            print("Available demos: 1, 2, 3, 4, 5, stats", file=sys.stderr)
            sys.exit(1)
    else:
        print("Cochrane Medical RAG System - Demonstrations")
        print("\nRunning all demos...\n")

        demos = [
            demo_1_simple_question,
            demo_2_statistical_evidence,
            demo_3_search_only,
            demo_4_high_quality_filter,
            demo_5_section_search,
            demo_stats,
        ]

        for demo in demos:
            try:
                demo()
            except Exception as e:
                print(f"\nError in {demo.__name__}: {e}", file=sys.stderr)

    print("\n" + "=" * 80)
    print("DEMOS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

