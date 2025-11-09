"""
Orchestrator class that combines all visualization components.
Provides high-level API for complete analysis pipeline.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from pathlib import Path

from .data_fetcher import EmbeddingDataFetcher
from .dimension_reducer import DimensionReducer
from .cluster_analyzer import ClusterAnalyzer
from .query_analyzer import QueryHitAnalyzer
from .visualizer import EmbeddingVisualizer
from .report_generator import AnalysisReportGenerator


class EmbeddingAnalyzer:
    """Orchestrates all visualization components for complete analysis."""
    
    def __init__(
        self,
        sample_size: int = 1000,
        random_seed: int = 42,
        n_neighbors: int = 15,
        min_dist: float = 0.1
    ):
        """
        Initialize the embedding analyzer.
        
        Args:
            sample_size: Default number of embeddings to sample
            random_seed: Random seed for reproducibility
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter
        """
        print("🔧 Initializing EmbeddingAnalyzer...")
        self.sample_size = sample_size
        self.random_seed = random_seed
        
        # Initialize components
        self.data_fetcher = EmbeddingDataFetcher()
        self.dimension_reducer = DimensionReducer(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            random_state=random_seed
        )
        self.cluster_analyzer = ClusterAnalyzer(random_state=random_seed)
        self.query_analyzer = QueryHitAnalyzer()
        self.visualizer = EmbeddingVisualizer()
        self.report_generator = AnalysisReportGenerator()
        
        # Storage for results
        self.embeddings = None
        self.metadata = None
        self.df = None
        self.umap_2d = None
        self.umap_3d = None
        self.clustering_results = None
        self.query_results = None
        
        print("✅ EmbeddingAnalyzer ready!")
    
    def run_full_analysis(
        self,
        limit: Optional[int] = None,
        test_queries: Optional[List[str]] = None,
        n_clusters: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline.
        
        Args:
            limit: Number of embeddings to analyze (None = use sample_size)
            test_queries: Optional list of test queries for hit analysis
            n_clusters: Optional number of clusters (None = auto-determine)
            
        Returns:
            Dictionary with all results and figures
        """
        print("🚀 Running full analysis pipeline...")
        
        # Step 1: Fetch data
        print("\n[1/5] Fetching embeddings...")
        self.embeddings, self.metadata, self.df = self.data_fetcher.fetch_embeddings(
            limit=limit or self.sample_size
        )
        
        if len(self.embeddings) == 0:
            raise ValueError("No embeddings found in Weaviate")
        
        # Step 2: Reduce dimensions
        print("\n[2/5] Reducing dimensions...")
        self.umap_2d, self.umap_3d = self.dimension_reducer.reduce_both(self.embeddings)
        
        # Step 3: Analyze clusters
        print("\n[3/5] Analyzing clusters...")
        self.clustering_results = self.cluster_analyzer.analyze_clusters(
            self.embeddings,
            self.metadata,
            n_clusters=n_clusters
        )
        
        # Step 4: Analyze queries (if provided)
        if test_queries:
            print("\n[4/5] Analyzing query hits...")
            self.query_results = self.query_analyzer.analyze_queries(
                test_queries,
                self.embeddings,
                self.metadata
            )
        else:
            print("\n[4/5] Skipping query analysis (no test queries provided)")
            self.query_results = None
        
        # Step 5: Generate visualizations
        print("\n[5/5] Generating visualizations...")
        figures = self._generate_all_figures()
        
        results = {
            'embeddings': self.embeddings,
            'metadata': self.metadata,
            'dataframe': self.df,
            'umap_2d': self.umap_2d,
            'umap_3d': self.umap_3d,
            'clustering_results': self.clustering_results,
            'query_results': self.query_results,
            'figures': figures
        }
        
        print("\n✅ Full analysis complete!")
        return results
    
    def quick_visualize(
        self,
        limit: int = 500,
        color_by: str = 'topic'
    ) -> Dict[str, Any]:
        """
        Quick visualization with minimal processing.
        
        Args:
            limit: Number of embeddings to visualize
            color_by: What to color by ('topic', 'quality_grade', 'cluster')
            
        Returns:
            Dictionary with basic results and figures
        """
        print("⚡ Running quick visualization...")
        
        # Fetch and reduce
        embeddings, metadata, df = self.data_fetcher.fetch_embeddings(limit=limit)
        umap_2d, umap_3d = self.dimension_reducer.reduce_both(embeddings)
        
        # Create basic visualizations
        visualizer = EmbeddingVisualizer()
        
        if color_by == 'topic':
            fig_2d = visualizer.plot_2d_by_topic(df, umap_2d)
        elif color_by == 'quality_grade':
            fig_2d = visualizer.plot_2d_by_quality(df, umap_2d)
        else:
            # Default to topic
            fig_2d = visualizer.plot_2d_by_topic(df, umap_2d)
        
        fig_3d = visualizer.plot_3d_interactive(df, umap_3d, color_by=color_by)
        
        return {
            'embeddings': embeddings,
            'metadata': metadata,
            'dataframe': df,
            'umap_2d': umap_2d,
            'umap_3d': umap_3d,
            'figures': {
                '2d': fig_2d,
                '3d': fig_3d
            }
        }
    
    def _generate_all_figures(self) -> Dict[str, Any]:
        """Generate all visualization figures."""
        figures = {}
        
        # Update dataframe with UMAP coordinates and clusters
        plot_df = self.df.copy()
        plot_df['x_2d'] = self.umap_2d[:, 0]
        plot_df['y_2d'] = self.umap_2d[:, 1]
        plot_df['x_3d'] = self.umap_3d[:, 0]
        plot_df['y_3d'] = self.umap_3d[:, 1]
        plot_df['z_3d'] = self.umap_3d[:, 2]
        plot_df['cluster'] = self.clustering_results['cluster_labels']
        
        # Add hit counts if query results available
        if self.query_results:
            hit_counts = self.query_results.get('hit_counts', {})
            plot_df['hit_count'] = [hit_counts.get(i, 0) for i in range(len(plot_df))]
        
        # Generate all plots
        figures['2d_by_topic'] = self.visualizer.plot_2d_by_topic(plot_df, self.umap_2d)
        figures['2d_by_quality'] = self.visualizer.plot_2d_by_quality(plot_df, self.umap_2d)
        figures['2d_by_cluster'] = self.visualizer.plot_2d_by_cluster(
            plot_df, 
            self.umap_2d, 
            self.clustering_results['cluster_labels']
        )
        figures['3d_interactive'] = self.visualizer.plot_3d_interactive(plot_df, self.umap_3d)
        figures['cluster_purity'] = self.visualizer.plot_cluster_purity(self.clustering_results)
        
        # Topic similarity
        topics = [m.get('topic_name', 'Unknown') for m in self.metadata]
        figures['topic_similarity'] = self.visualizer.plot_topic_similarity_matrix(
            self.embeddings,
            topics
        )
        
        # Query analysis plots (if available)
        if self.query_results:
            figures['query_hits'] = self.visualizer.plot_query_hits(
                plot_df,
                self.umap_2d,
                self.query_results
            )
            figures['hit_frequency'] = self.visualizer.plot_hit_frequency(self.query_results)
        
        return figures
    
    def generate_report(
        self,
        output_dir: Optional[Path] = None,
        save_html: bool = False
    ):
        """
        Generate and save analysis report.
        
        Args:
            output_dir: Directory to save reports (None = current directory)
            save_html: Whether to save figures as HTML files
        """
        if self.clustering_results is None:
            raise ValueError("Must run analysis first. Call run_full_analysis()")
        
        output_dir = output_dir or Path("embedding_analysis")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate text report
        report_path = output_dir / "analysis_report.txt"
        self.report_generator.generate_text_report(
            self.clustering_results,
            self.query_results,
            report_path
        )
        
        # Export JSON
        json_path = output_dir / "analysis_results.json"
        self.report_generator.export_json(
            self.clustering_results,
            self.query_results,
            json_path
        )
        
        # Save HTML figures if requested
        if save_html and self._generate_all_figures():
            figures = self._generate_all_figures()
            for name, fig in figures.items():
                html_path = output_dir / f"{name}.html"
                self.visualizer.save_html(fig, str(html_path))
        
        print(f"✅ Reports saved to {output_dir}/")
    
    def close(self):
        """Close all connections."""
        self.data_fetcher.close()
        self.query_analyzer.close()

