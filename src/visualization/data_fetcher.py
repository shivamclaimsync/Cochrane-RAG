"""
Data fetcher for retrieving embeddings and metadata from Weaviate.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from collections import Counter

from src.indexing.weaviate_client import WeaviateManager
from src.indexing.config import EmbeddingConfig
from src.retrieving.embedder_factory import get_embedder


class EmbeddingDataFetcher:
    """Fetches embeddings and metadata from Weaviate for analysis."""
    
    def __init__(self):
        """Initialize the data fetcher with Weaviate connection."""
        print("🔧 Initializing EmbeddingDataFetcher...")
        self.embedding_config = EmbeddingConfig()
        embedder = get_embedder(self.embedding_config, mode="query")
        self.weaviate_manager = WeaviateManager(embedder=embedder)
        self.collection = self.weaviate_manager.client.collections.get("CochraneChunk")
        print("✅ EmbeddingDataFetcher ready!")
    
    def fetch_embeddings(
        self, 
        limit: Optional[int] = None,
        return_dataframe: bool = True
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], Optional[pd.DataFrame]]:
        """
        Fetch embeddings and metadata from Weaviate.
        
        Args:
            limit: Maximum number of chunks to fetch (None = all)
            return_dataframe: Whether to also return a pandas DataFrame
            
        Returns:
            Tuple of (embeddings array, metadata list, optional DataFrame)
        """
        print(f"📥 Fetching embeddings from Weaviate...")
        
        # Get total count
        total_count = self.collection.aggregate.over_all(total_count=True).total_count or 0
        print(f"   Total chunks in store: {total_count}")
        
        fetch_limit = limit or total_count
        print(f"   Fetching {fetch_limit} chunks...")
        
        # Fetch objects with vectors
        response = self.collection.query.fetch_objects(
            limit=fetch_limit,
            include_vector=True
        )
        
        embeddings = []
        metadata_list = []
        
        for obj in response.objects:
            # Get vector
            if hasattr(obj, 'vector') and obj.vector:
                vector = obj.vector.get('default') or obj.vector
                if vector:
                    embeddings.append(vector)
                    metadata_list.append({
                        'chunk_id': obj.properties.get('chunk_id', ''),
                        'document_id': obj.properties.get('document_id', ''),
                        'level': obj.properties.get('level', ''),
                        'section_name': obj.properties.get('section_name', ''),
                        'subsection_name': obj.properties.get('subsection_name', ''),
                        'is_statistical': obj.properties.get('is_statistical', False),
                        'content': obj.properties.get('content', '')[:200],  # First 200 chars
                    })
        
        # Get document metadata for topic and quality
        doc_ids = list(set(m['document_id'] for m in metadata_list))
        doc_metadata = self.weaviate_manager.get_batch_document_metadata(doc_ids)
        
        # Enrich metadata with document info
        for meta in metadata_list:
            doc_id = meta['document_id']
            if doc_id in doc_metadata:
                doc_info = doc_metadata[doc_id]
                meta['topic_name'] = doc_info.get('topic_name', 'Unknown')
                meta['quality_grade'] = doc_info.get('quality_grade', 'Unknown')
                meta['title'] = doc_info.get('title', '')
            else:
                meta['topic_name'] = 'Unknown'
                meta['quality_grade'] = 'Unknown'
                meta['title'] = ''
        
        embeddings_array = np.array(embeddings)
        print(f"✅ Fetched {len(embeddings)} embeddings (shape: {embeddings_array.shape})")
        
        # Create DataFrame if requested
        df = None
        if return_dataframe and metadata_list:
            df = pd.DataFrame(metadata_list)
            print(f"✅ Created DataFrame with {len(df)} rows")
        
        return embeddings_array, metadata_list, df
    
    def get_sample_by_topic(
        self, 
        topic: str, 
        sample_size: int = 100
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], Optional[pd.DataFrame]]:
        """
        Get a sample of embeddings for a specific topic.
        
        Args:
            topic: Topic name to filter by
            sample_size: Maximum number of samples to return
            
        Returns:
            Tuple of (embeddings array, metadata list, optional DataFrame)
        """
        print(f"📥 Fetching samples for topic: {topic}...")
        
        # Fetch with topic filter
        from weaviate.classes.query import Filter
        response = self.collection.query.fetch_objects(
            limit=sample_size,
            include_vector=True,
            filters=Filter.by_property("document_id").like(f"*{topic}*")  # Approximate filter
        )
        
        embeddings = []
        metadata_list = []
        
        for obj in response.objects:
            if hasattr(obj, 'vector') and obj.vector:
                vector = obj.vector.get('default') or obj.vector
                if vector:
                    embeddings.append(vector)
                    metadata_list.append({
                        'chunk_id': obj.properties.get('chunk_id', ''),
                        'document_id': obj.properties.get('document_id', ''),
                        'level': obj.properties.get('level', ''),
                        'section_name': obj.properties.get('section_name', ''),
                        'subsection_name': obj.properties.get('subsection_name', ''),
                        'is_statistical': obj.properties.get('is_statistical', False),
                        'content': obj.properties.get('content', '')[:200],
                    })
        
        # Enrich with document metadata
        doc_ids = list(set(m['document_id'] for m in metadata_list))
        doc_metadata = self.weaviate_manager.get_batch_document_metadata(doc_ids)
        
        for meta in metadata_list:
            doc_id = meta['document_id']
            if doc_id in doc_metadata:
                doc_info = doc_metadata[doc_id]
                meta['topic_name'] = doc_info.get('topic_name', 'Unknown')
                meta['quality_grade'] = doc_info.get('quality_grade', 'Unknown')
                meta['title'] = doc_info.get('title', '')
            else:
                meta['topic_name'] = 'Unknown'
                meta['quality_grade'] = 'Unknown'
                meta['title'] = ''
        
        embeddings_array = np.array(embeddings) if embeddings else np.array([])
        df = pd.DataFrame(metadata_list) if metadata_list else pd.DataFrame()
        
        print(f"✅ Fetched {len(embeddings)} samples for topic: {topic}")
        return embeddings_array, metadata_list, df
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the embedding store.
        
        Returns:
            Dictionary with statistics
        """
        print("📊 Computing statistics...")
        
        stats = self.weaviate_manager.get_processing_stats()
        
        # Get sample to compute topic distribution
        embeddings, metadata, _ = self.fetch_embeddings(limit=1000, return_dataframe=False)
        
        topics = [m.get('topic_name', 'Unknown') for m in metadata]
        topic_counts = Counter(topics)
        
        quality_grades = [m.get('quality_grade', 'Unknown') for m in metadata]
        quality_counts = Counter(quality_grades)
        
        levels = [m.get('level', 'Unknown') for m in metadata]
        level_counts = Counter(levels)
        
        stats['topic_distribution'] = dict(topic_counts)
        stats['quality_distribution'] = dict(quality_counts)
        stats['level_distribution'] = dict(level_counts)
        stats['sample_size'] = len(metadata)
        
        print("✅ Statistics computed")
        return stats
    
    def close(self):
        """Close Weaviate connection."""
        self.weaviate_manager.close()

