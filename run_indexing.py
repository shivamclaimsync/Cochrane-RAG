#!/usr/bin/env python3
"""
Script to clear vector store and run indexing on processed documents from the output directory.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.indexing.indexing_pipeline import IndexingPipeline


def main():
    """Clear vector store and index files from output directory."""
    # Get output directory
    output_dir = Path(__file__).parent / 'output'
    
    if not output_dir.exists():
        print(f"Error: Output directory not found: {output_dir}")
        sys.exit(1)
    
    # Initialize pipeline
    print("Initializing indexing pipeline...")
    pipeline = IndexingPipeline()
    
    try:
        # Clear the vector store
        print("\n" + "="*60)
        print("CLEARING VECTOR STORE")
        print("="*60)
        pipeline.weaviate_manager.clear_all_collections()
        
        # Index up to 500 files from output directory
        print("\n" + "="*60)
        print("STARTING INDEXING")
        print("="*60)
        print(f"Directory: {output_dir}")
        print("Limit: 500 files\n")
        
        pipeline.index_processed_documents(
            processed_dir=output_dir,
            skip_processed=False,  # Since we cleared, skip_processed doesn't matter
            limit=500
        )
        
        print("\n✓ Indexing completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during indexing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()

