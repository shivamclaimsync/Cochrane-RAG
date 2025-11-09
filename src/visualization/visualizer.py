"""
Plotly visualizations for embedding analysis.
All methods return Plotly figure objects for notebook display.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class EmbeddingVisualizer:
    """Generates Plotly visualizations for embedding analysis."""
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize the visualizer.
        
        Args:
            width: Default figure width
            height: Default figure height
        """
        self.width = width
        self.height = height
    
    def plot_2d_by_topic(
        self,
        df: pd.DataFrame,
        umap_2d: np.ndarray,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create 2D scatter plot colored by topic.
        
        Args:
            df: DataFrame with metadata
            umap_2d: 2D UMAP coordinates
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        plot_df = df.copy()
        plot_df['x'] = umap_2d[:, 0]
        plot_df['y'] = umap_2d[:, 1]
        
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='topic_name',
            title=title or 'Embedding Space Visualization (2D UMAP) - Colored by Topic',
            labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'},
            hover_data=['quality_grade', 'section_name', 'level'],
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_2d_by_quality(
        self,
        df: pd.DataFrame,
        umap_2d: np.ndarray,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create 2D scatter plot colored by quality grade.
        
        Args:
            df: DataFrame with metadata
            umap_2d: 2D UMAP coordinates
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        plot_df = df.copy()
        plot_df['x'] = umap_2d[:, 0]
        plot_df['y'] = umap_2d[:, 1]
        
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='quality_grade',
            title=title or 'Embedding Space Visualization (2D UMAP) - Colored by Quality Grade',
            labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'},
            hover_data=['topic_name', 'section_name'],
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_2d_by_cluster(
        self,
        df: pd.DataFrame,
        umap_2d: np.ndarray,
        cluster_labels: List[int],
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create 2D scatter plot colored by cluster.
        
        Args:
            df: DataFrame with metadata
            umap_2d: 2D UMAP coordinates
            cluster_labels: Cluster assignment for each point
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        plot_df = df.copy()
        plot_df['x'] = umap_2d[:, 0]
        plot_df['y'] = umap_2d[:, 1]
        plot_df['cluster'] = cluster_labels
        
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='cluster',
            title=title or f'Embedding Clusters (2D UMAP) - {n_clusters} Clusters',
            labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'},
            hover_data=['topic_name', 'quality_grade'],
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_3d_interactive(
        self,
        df: pd.DataFrame,
        umap_3d: np.ndarray,
        color_by: str = 'cluster',
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create 3D interactive scatter plot.
        
        Args:
            df: DataFrame with metadata
            umap_3d: 3D UMAP coordinates
            color_by: Column to color by ('cluster', 'topic', 'quality_grade')
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        plot_df = df.copy()
        plot_df['x'] = umap_3d[:, 0]
        plot_df['y'] = umap_3d[:, 1]
        plot_df['z'] = umap_3d[:, 2]
        
        # Create hover text
        hover_text = [
            f"Topic: {t}<br>Quality: {q}<br>Section: {s}<br>Level: {l}" 
            for t, q, s, l in zip(
                plot_df.get('topic', [''] * len(plot_df)),
                plot_df.get('quality_grade', [''] * len(plot_df)),
                plot_df.get('section_name', [''] * len(plot_df)),
                plot_df.get('level', [''] * len(plot_df))
            )
        ]
        
        fig = go.Figure(data=go.Scatter3d(
            x=plot_df['x'],
            y=plot_df['y'],
            z=plot_df['z'],
            mode='markers',
            marker=dict(
                size=5,
                color=plot_df.get(color_by, 0),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=color_by.replace('_', ' ').title())
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title or 'Embedding Space Visualization (3D UMAP)',
            scene=dict(
                xaxis_title='UMAP Dimension 1',
                yaxis_title='UMAP Dimension 2',
                zaxis_title='UMAP Dimension 3'
            ),
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_query_hits(
        self,
        df: pd.DataFrame,
        umap_2d: np.ndarray,
        query_results: Dict[str, Any],
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Visualize which embeddings are hit by queries.
        
        Args:
            df: DataFrame with metadata
            umap_2d: 2D UMAP coordinates
            query_results: Results from QueryHitAnalyzer
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        plot_df = df.copy()
        plot_df['x'] = umap_2d[:, 0]
        plot_df['y'] = umap_2d[:, 1]
        
        # Add hit counts
        hit_counts = query_results.get('hit_counts', {})
        plot_df['hit_count'] = [hit_counts.get(i, 0) for i in range(len(plot_df))]
        
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='hit_count',
            size='hit_count',
            title=title or 'Query Hit Analysis - Which Embeddings Are Retrieved Most Often',
            labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'},
            hover_data=['topic_name', 'quality_grade', 'section_name'],
            color_continuous_scale='YlOrRd',
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_hit_frequency(
        self,
        query_results: Dict[str, Any],
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Plot distribution of hit frequencies.
        
        Args:
            query_results: Results from QueryHitAnalyzer
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        hit_counts = query_results.get('hit_counts', {})
        hit_counts_list = [c for c in hit_counts.values() if c > 0]
        
        if not hit_counts_list:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No hits recorded",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(title=title or 'Hit Frequency Distribution')
            return fig
        
        fig = px.histogram(
            x=hit_counts_list,
            title=title or 'Query Hit Frequency Distribution',
            labels={'x': 'Number of Times Retrieved', 'count': 'Number of Chunks'},
            nbins=20,
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_topic_similarity_matrix(
        self,
        embeddings: np.ndarray,
        topics: List[str],
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create heatmap showing similarity between topics.
        
        Args:
            embeddings: Embedding vectors
            topics: Topic label for each embedding
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        unique_topics = list(set(topics))
        if len(unique_topics) <= 1:
            fig = go.Figure()
            fig.add_annotation(
                text="Need at least 2 topics for similarity matrix",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(title=title or 'Topic Similarity Matrix')
            return fig
        
        # Calculate average embedding per topic
        topic_embeddings = {}
        for topic in unique_topics:
            topic_mask = np.array([t == topic for t in topics])
            topic_indices = np.where(topic_mask)[0]
            if len(topic_indices) > 0:
                topic_avg_embedding = embeddings[topic_indices].mean(axis=0)
                topic_embeddings[topic] = topic_avg_embedding
        
        # Calculate cosine similarity between topics
        similarity_matrix = np.zeros((len(unique_topics), len(unique_topics)))
        for i, topic1 in enumerate(unique_topics):
            for j, topic2 in enumerate(unique_topics):
                if topic1 in topic_embeddings and topic2 in topic_embeddings:
                    vec1 = topic_embeddings[topic1]
                    vec2 = topic_embeddings[topic2]
                    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    similarity_matrix[i, j] = similarity
        
        fig = px.imshow(
            similarity_matrix,
            labels=dict(x="Topic", y="Topic", color="Cosine Similarity"),
            x=unique_topics,
            y=unique_topics,
            title=title or "Topic Embedding Similarity Matrix",
            color_continuous_scale='RdYlBu_r',
            width=self.width,
            height=self.height
        )
        return fig
    
    def plot_cluster_purity(
        self,
        clustering_results: Dict[str, Any],
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Visualize cluster purity scores.
        
        Args:
            clustering_results: Results from ClusterAnalyzer
            title: Optional custom title
            
        Returns:
            Plotly figure object
        """
        cluster_purities = clustering_results.get('cluster_purities', {})
        if not cluster_purities:
            fig = go.Figure()
            fig.add_annotation(
                text="No cluster purity data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(title=title or 'Cluster Purity Analysis')
            return fig
        
        cluster_ids = list(cluster_purities.keys())
        purities = [cluster_purities[cid]['purity'] for cid in cluster_ids]
        dominant_topics = [cluster_purities[cid]['dominant_topic'] for cid in cluster_ids]
        
        fig = go.Figure(data=go.Bar(
            x=[f"Cluster {cid}" for cid in cluster_ids],
            y=purities,
            text=dominant_topics,
            textposition='outside',
            marker=dict(color=purities, colorscale='Viridis')
        ))
        
        fig.update_layout(
            title=title or 'Cluster Purity Analysis (Higher = More Topic Coherence)',
            xaxis_title='Cluster ID',
            yaxis_title='Purity Score',
            width=self.width,
            height=self.height
        )
        return fig
    
    def save_html(self, fig: go.Figure, filepath: str):
        """
        Save a figure to HTML file.
        
        Args:
            fig: Plotly figure object
            filepath: Path to save HTML file
        """
        fig.write_html(filepath)

