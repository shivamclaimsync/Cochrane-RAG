"""
Query hit analysis to understand which embeddings are retrieved.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict, Counter

from src.retrieving.retriever import CochraneRetriever


class QueryHitAnalyzer:
    """Analyzes which embeddings are hit by queries."""
    
    def __init__(self):
        """Initialize the query analyzer."""
        print("🔧 Initializing QueryHitAnalyzer...")
        self.retriever = CochraneRetriever()
        print("✅ QueryHitAnalyzer ready!")
    
    def analyze_queries(
        self,
        queries: List[str],
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        limit_per_query: int = 10,
        use_hybrid: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze which embeddings are hit by test queries.
        
        Args:
            queries: List of test queries to analyze
            embeddings: Stored embeddings
            metadata: Metadata for each embedding
            limit_per_query: Number of results to retrieve per query
            use_hybrid: Whether to use hybrid search
            
        Returns:
            Dictionary with query hit analysis results
        """
        print(f"🎯 Analyzing query hit patterns for {len(queries)} queries...")
        
        # Create mapping from chunk_id to index
        chunk_id_to_index = {m['chunk_id']: i for i, m in enumerate(metadata)}
        hit_counts = defaultdict(int)
        query_results = []
        
        for query in queries:
            try:
                # Perform retrieval
                results = self.retriever.search(
                    query, 
                    limit=limit_per_query, 
                    use_hybrid=use_hybrid
                )
                
                # Track hits
                hit_indices = []
                distances = []
                
                for result in results:
                    chunk_id = result.chunk_id
                    if chunk_id in chunk_id_to_index:
                        idx = chunk_id_to_index[chunk_id]
                        hit_counts[idx] += 1
                        hit_indices.append(idx)
                        distances.append(result.distance)
                
                query_results.append({
                    'query': query,
                    'n_results': len(results),
                    'hit_indices': hit_indices,
                    'distances': distances,
                    'avg_distance': float(np.mean(distances)) if distances else None,
                    'min_distance': float(np.min(distances)) if distances else None,
                    'max_distance': float(np.max(distances)) if distances else None
                })
                
            except Exception as e:
                print(f"   ⚠️ Error processing query '{query[:50]}...': {e}")
                query_results.append({
                    'query': query,
                    'n_results': 0,
                    'hit_indices': [],
                    'distances': [],
                    'error': str(e)
                })
                continue
        
        # Analyze hit patterns
        most_hit_indices = sorted(hit_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Get metadata for most hit chunks
        most_hit_chunks = []
        for idx, count in most_hit_indices:
            if idx < len(metadata):
                most_hit_chunks.append({
                    'index': idx,
                    'hit_count': count,
                    'metadata': metadata[idx]
                })
        
        # Calculate statistics
        hit_counts_list = list(hit_counts.values())
        stats = {
            'total_unique_hits': len(hit_counts),
            'total_queries': len(queries),
            'avg_hits_per_query': float(np.mean([r['n_results'] for r in query_results if r['n_results'] > 0])) if query_results else 0.0,
            'max_hit_count': int(max(hit_counts_list)) if hit_counts_list else 0,
            'avg_hit_count': float(np.mean(hit_counts_list)) if hit_counts_list else 0.0
        }
        
        results = {
            'query_results': query_results,
            'hit_counts': dict(hit_counts),
            'most_hit_chunks': most_hit_chunks,
            'statistics': stats
        }
        
        print(f"✅ Query analysis complete")
        print(f"   Unique chunks hit: {len(hit_counts)}")
        if most_hit_chunks:
            print(f"   Most hit chunk: {most_hit_chunks[0]['hit_count']} times")
        
        return results
    
    def get_hit_statistics(self, query_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary statistics from query results.
        
        Args:
            query_results: Results from analyze_queries()
            
        Returns:
            Dictionary with statistics
        """
        return query_results.get('statistics', {})
    
    def get_most_hit_chunks(
        self, 
        query_results: Dict[str, Any],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most frequently hit chunks.
        
        Args:
            query_results: Results from analyze_queries()
            top_n: Number of top chunks to return
            
        Returns:
            List of most hit chunks with metadata
        """
        return query_results.get('most_hit_chunks', [])[:top_n]
    
    def analyze_query_coverage(
        self,
        query_results: Dict[str, Any],
        total_embeddings: int
    ) -> Dict[str, Any]:
        """
        Analyze how much of the embedding space is covered by queries.
        
        Args:
            query_results: Results from analyze_queries()
            total_embeddings: Total number of embeddings in store
            
        Returns:
            Dictionary with coverage statistics
        """
        hit_counts = query_results.get('hit_counts', {})
        unique_hits = len(hit_counts)
        
        coverage = {
            'unique_chunks_hit': unique_hits,
            'total_chunks': total_embeddings,
            'coverage_percentage': (unique_hits / total_embeddings * 100) if total_embeddings > 0 else 0.0,
            'queries_analyzed': query_results.get('statistics', {}).get('total_queries', 0)
        }
        
        return coverage
    
    def close(self):
        """Close retriever connection."""
        self.retriever.close()

