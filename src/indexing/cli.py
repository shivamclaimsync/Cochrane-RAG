import argparse
from pathlib import Path
from src.indexing.indexing_pipeline import IndexingPipeline
from src.indexing.weaviate_client import WeaviateManager
from src.indexing.config import PathConfig


def index_command(args):
    print("Starting indexing process...")
    
    processed_dir = Path(args.input_dir) if args.input_dir else PathConfig.PROCESSED_DATA_DIR
    
    pipeline = IndexingPipeline()
    
    try:
        pipeline.index_processed_documents(
            processed_dir=processed_dir,
            skip_processed=not args.force,
            limit=args.limit
        )
    finally:
        pipeline.close()


def reindex_command(args):
    print("Starting reindex process (force mode)...")
    
    processed_dir = Path(args.input_dir) if args.input_dir else PathConfig.PROCESSED_DATA_DIR
    
    pipeline = IndexingPipeline()
    
    try:
        pipeline.index_processed_documents(
            processed_dir=processed_dir,
            skip_processed=False,
            limit=args.limit
        )
    finally:
        pipeline.close()


def stats_command(args):
    print("Fetching indexing statistics...\n")
    
    manager = WeaviateManager()
    
    try:
        stats = manager.get_processing_stats()
        
        print("="*60)
        print("WEAVIATE DATABASE STATISTICS")
        print("="*60)
        print(f"Total Chunks: {stats.get('total_chunks', 0)}")
        print(f"Total Documents Processed: {stats.get('total_documents_processed', 0)}")
        
        if 'chunks_by_level' in stats:
            print(f"\nChunks by Level:")
            for level, count in stats['chunks_by_level'].items():
                print(f"  - {level}: {count}")
        
        print("="*60)
    finally:
        manager.close()


def reset_command(args):
    if not args.confirm:
        response = input("WARNING: This will delete all chunks and history from Weaviate. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Reset cancelled.")
            return
    
    print("Resetting Weaviate collections...")
    
    manager = WeaviateManager()
    
    try:
        if manager.client.collections.exists(manager.config.COLLECTION_CHUNKS):
            manager.client.collections.delete(manager.config.COLLECTION_CHUNKS)
            print(f"✓ Deleted {manager.config.COLLECTION_CHUNKS} collection")
        
        if manager.client.collections.exists(manager.config.COLLECTION_HISTORY):
            manager.client.collections.delete(manager.config.COLLECTION_HISTORY)
            print(f"✓ Deleted {manager.config.COLLECTION_HISTORY} collection")
        
        manager._create_schema()
        print("✓ Recreated collections with fresh schema")
        print("\nReset complete!")
        
    finally:
        manager.close()


def main():
    parser = argparse.ArgumentParser(
        description='Cochrane RAG Multi-Level Chunking and Indexing CLI'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    index_parser = subparsers.add_parser('index', help='Index processed documents')
    index_parser.add_argument(
        '--input-dir',
        type=str,
        help='Path to processed data directory (default: processed_data/)'
    )
    index_parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of documents to process'
    )
    index_parser.add_argument(
        '--force',
        action='store_true',
        help='Force reindex already processed documents'
    )
    index_parser.set_defaults(func=index_command)
    
    reindex_parser = subparsers.add_parser('reindex', help='Force reindex all documents')
    reindex_parser.add_argument(
        '--input-dir',
        type=str,
        help='Path to processed data directory'
    )
    reindex_parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of documents to process'
    )
    reindex_parser.set_defaults(func=reindex_command)
    
    stats_parser = subparsers.add_parser('stats', help='Show indexing statistics')
    stats_parser.set_defaults(func=stats_command)
    
    reset_parser = subparsers.add_parser('reset', help='Clear Weaviate collections')
    reset_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    reset_parser.set_defaults(func=reset_command)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

