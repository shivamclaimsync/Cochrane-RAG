"""
Command-line interface for retrieval system.
"""

import argparse
from src.retrieving.retriever import CochraneRetriever


def search_command(args):
    """Execute search command."""
    retriever = CochraneRetriever()
    
    try:
        results = retriever.search(
            query=args.query,
            limit=args.limit,
            level=args.level,
            topic=args.topic,
            quality_grade=args.quality,
            statistical_only=args.statistical,
            section=args.section
        )
        
        print(retriever.format_results(results))
        
        # Show individual results
        if args.verbose:
            for result in results:
                print(result)
        
    finally:
        retriever.close()


def demo_command(args):
    """Run demo queries."""
    retriever = CochraneRetriever()
    
    demo_queries = [
        ("What are the effects of corticosteroids on asthma symptoms?", {}),
        ("Efficacy of antibiotics for preventing infections", {"section": "results"}),
        ("Statistical significance of treatment outcomes", {"statistical_only": True}),
        ("Interventions for allergic rhinitis", {"topic": "Allergy & Intolerance"}),
    ]
    
    try:
        for query, kwargs in demo_queries:
            print("\n" + "="*80)
            print(f"DEMO QUERY: {query}")
            print("="*80)
            
            results = retriever.search(query=query, limit=3, **kwargs)
            print(retriever.format_results(results))
            
            if args.wait:
                input("\nPress Enter to continue...")
    
    finally:
        retriever.close()


def main():
    parser = argparse.ArgumentParser(
        description="Cochrane RAG Retrieval System"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search the knowledge base')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--limit', type=int, default=5, help='Number of results')
    search_parser.add_argument('--level', type=str, help='Filter by level (DOCUMENT, SECTION, SUBSECTION, PARAGRAPH)')
    search_parser.add_argument('--topic', type=str, help='Filter by topic')
    search_parser.add_argument('--quality', type=str, help='Filter by quality grade (A, B, C)')
    search_parser.add_argument('--statistical', action='store_true', help='Only statistical content')
    search_parser.add_argument('--section', type=str, help='Filter by section (methods, results, etc.)')
    search_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    search_parser.set_defaults(func=search_command)
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo queries')
    demo_parser.add_argument('--wait', action='store_true', help='Wait between queries')
    demo_parser.set_defaults(func=demo_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == '__main__':
    main()

