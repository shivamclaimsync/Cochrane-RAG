"""
Report generator for embedding analysis results.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json


class AnalysisReportGenerator:
    """Generates text and JSON reports from analysis results."""
    
    def __init__(self):
        """Initialize the report generator."""
        pass
    
    def generate_text_report(
        self,
        clustering_results: Dict[str, Any],
        query_results: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate a text report with analysis findings.
        
        Args:
            clustering_results: Results from ClusterAnalyzer
            query_results: Optional results from QueryHitAnalyzer
            output_path: Optional path to save report
            
        Returns:
            Report text as string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("WEAVIATE EMBEDDING STORE ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Clustering Analysis
        lines.append("CLUSTERING ANALYSIS")
        lines.append("-" * 80)
        lines.append(f"Number of Clusters: {clustering_results.get('n_clusters', 'N/A')}")
        lines.append(f"Silhouette Score: {clustering_results.get('silhouette_score', 0):.3f}")
        lines.append(f"Average Cluster Purity: {clustering_results.get('average_purity', 0):.3f}")
        lines.append("")
        
        topic_counts = clustering_results.get('topic_counts', {})
        if topic_counts:
            lines.append("Topic Distribution:")
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                lines.append(f"  {topic}: {count} chunks")
            lines.append("")
        
        cluster_purities = clustering_results.get('cluster_purities', {})
        if cluster_purities:
            lines.append("Cluster Purity Details:")
            for cluster_id, info in cluster_purities.items():
                lines.append(f"  Cluster {cluster_id}:")
                lines.append(f"    Purity: {info.get('purity', 0):.3f}")
                lines.append(f"    Dominant Topic: {info.get('dominant_topic', 'N/A')}")
                topic_dist = info.get('topic_distribution', {})
                if topic_dist:
                    lines.append(f"    Topic Distribution: {topic_dist}")
            lines.append("")
        
        # Query Analysis
        if query_results:
            lines.append("QUERY HIT ANALYSIS")
            lines.append("-" * 80)
            stats = query_results.get('statistics', {})
            lines.append(f"Total Queries Analyzed: {stats.get('total_queries', 0)}")
            lines.append(f"Unique Chunks Hit: {stats.get('total_unique_hits', 0)}")
            avg_hits = stats.get('avg_hits_per_query', 0)
            lines.append(f"Average Results per Query: {avg_hits:.1f}")
            lines.append("")
            
            most_hit_chunks = query_results.get('most_hit_chunks', [])
            if most_hit_chunks:
                lines.append("Most Frequently Retrieved Chunks:")
                for i, chunk_info in enumerate(most_hit_chunks[:10], 1):
                    meta = chunk_info.get('metadata', {})
                    lines.append(f"  {i}. Hit {chunk_info.get('hit_count', 0)} times")
                    lines.append(f"     Topic: {meta.get('topic_name', 'Unknown')}")
                    lines.append(f"     Section: {meta.get('section_name', 'Unknown')}")
                    lines.append(f"     Level: {meta.get('level', 'Unknown')}")
                    lines.append("")
        
        lines.append("=" * 80)
        
        report_text = "\n".join(lines)
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report_text)
            print(f"✅ Report saved to {output_path}")
        
        return report_text
    
    def export_json(
        self,
        clustering_results: Dict[str, Any],
        query_results: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export analysis results to JSON.
        
        Args:
            clustering_results: Results from ClusterAnalyzer
            query_results: Optional results from QueryHitAnalyzer
            output_path: Optional path to save JSON
            
        Returns:
            Combined results dictionary
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'clustering_analysis': clustering_results,
        }
        
        if query_results:
            results['query_analysis'] = query_results
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Convert numpy types to native Python types for JSON serialization
            def convert_types(obj):
                if isinstance(obj, dict):
                    return {k: convert_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(item) for item in obj]
                elif hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif isinstance(obj, (np.integer, np.floating)):
                    return obj.item()
                else:
                    return obj
            
            import numpy as np
            results = convert_types(results)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"✅ Results exported to {output_path}")
        
        return results
    
    def get_summary_stats(
        self,
        clustering_results: Dict[str, Any],
        query_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics from analysis results.
        
        Args:
            clustering_results: Results from ClusterAnalyzer
            query_results: Optional results from QueryHitAnalyzer
            
        Returns:
            Dictionary with summary statistics
        """
        stats = {
            'clustering': {
                'n_clusters': clustering_results.get('n_clusters', 0),
                'silhouette_score': clustering_results.get('silhouette_score', 0.0),
                'average_purity': clustering_results.get('average_purity', 0.0),
                'n_topics': len(clustering_results.get('topic_counts', {}))
            }
        }
        
        if query_results:
            query_stats = query_results.get('statistics', {})
            stats['queries'] = {
                'total_queries': query_stats.get('total_queries', 0),
                'unique_hits': query_stats.get('total_unique_hits', 0),
                'avg_hits_per_query': query_stats.get('avg_hits_per_query', 0.0),
                'max_hit_count': query_stats.get('max_hit_count', 0)
            }
        
        return stats

