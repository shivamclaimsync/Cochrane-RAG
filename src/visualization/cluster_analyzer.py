"""
Cluster analysis for embeddings to validate topic clustering.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict, Counter
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler


class ClusterAnalyzer:
    """Analyzes clustering patterns in embeddings."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the cluster analyzer.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.scaler = StandardScaler()
    
    def analyze_clusters(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        n_clusters: Optional[int] = None,
        method: str = 'kmeans'
    ) -> Dict[str, Any]:
        """
        Analyze clustering of embeddings.
        
        Args:
            embeddings: Embedding vectors
            metadata: Metadata for each embedding
            n_clusters: Number of clusters (None = auto-determine from topics)
            method: Clustering method ('kmeans' or 'dbscan')
            
        Returns:
            Dictionary with clustering analysis results
        """
        print("🔍 Analyzing clustering patterns...")
        
        # Extract topics
        topics = [m.get('topic_name', 'Unknown') for m in metadata]
        topic_counts = Counter(topics)
        
        print(f"   Found {len(topic_counts)} unique topics")
        print(f"   Top topics: {dict(topic_counts.most_common(5))}")
        
        # Determine number of clusters
        if n_clusters is None:
            n_clusters = min(10, len(topic_counts), max(2, len(embeddings) // 50))
        
        # Standardize embeddings
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        # Perform clustering
        if method == 'kmeans':
            cluster_labels = self._kmeans_cluster(embeddings_scaled, n_clusters)
        elif method == 'dbscan':
            cluster_labels = self._dbscan_cluster(embeddings_scaled)
            n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        # Calculate silhouette score
        silhouette = silhouette_score(embeddings_scaled, cluster_labels)
        
        # Analyze topic distribution in clusters
        cluster_purities = self.calculate_purity(cluster_labels, topics)
        
        # Get cluster topic distributions
        cluster_topic_dist = self.get_cluster_topics(cluster_labels, topics)
        
        avg_purity = np.mean([p['purity'] for p in cluster_purities.values()])
        
        results = {
            'n_clusters': n_clusters,
            'silhouette_score': float(silhouette),
            'cluster_labels': cluster_labels.tolist(),
            'cluster_purities': cluster_purities,
            'average_purity': float(avg_purity),
            'topic_counts': dict(topic_counts),
            'cluster_topic_distribution': {
                str(k): dict(v) for k, v in cluster_topic_dist.items()
            },
            'method': method
        }
        
        print(f"✅ Clustering analysis complete")
        print(f"   Silhouette score: {silhouette:.3f}")
        print(f"   Average cluster purity: {avg_purity:.3f}")
        
        return results
    
    def _kmeans_cluster(self, embeddings: np.ndarray, n_clusters: int) -> np.ndarray:
        """Perform KMeans clustering."""
        kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
        return kmeans.fit_predict(embeddings)
    
    def _dbscan_cluster(self, embeddings: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
        """Perform DBSCAN clustering."""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        return dbscan.fit_predict(embeddings)
    
    def calculate_purity(
        self,
        cluster_labels: np.ndarray,
        topics: List[str]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Calculate cluster purity (how well clusters match topics).
        
        Args:
            cluster_labels: Cluster assignment for each embedding
            topics: Topic label for each embedding
            
        Returns:
            Dictionary mapping cluster_id to purity information
        """
        cluster_topic_dist = defaultdict(lambda: defaultdict(int))
        
        for label, topic in zip(cluster_labels, topics):
            if label != -1:  # Ignore noise points in DBSCAN
                cluster_topic_dist[label][topic] += 1
        
        cluster_purities = {}
        for cluster_id, topic_dist in cluster_topic_dist.items():
            total = sum(topic_dist.values())
            if total > 0:
                dominant_topic_count = max(topic_dist.values())
                purity = dominant_topic_count / total
                dominant_topic = max(topic_dist.items(), key=lambda x: x[1])[0]
                
                cluster_purities[cluster_id] = {
                    'purity': float(purity),
                    'dominant_topic': dominant_topic,
                    'topic_distribution': dict(topic_dist)
                }
        
        return cluster_purities
    
    def get_cluster_topics(
        self,
        cluster_labels: np.ndarray,
        topics: List[str]
    ) -> Dict[int, Dict[str, int]]:
        """
        Get topic distribution for each cluster.
        
        Args:
            cluster_labels: Cluster assignment for each embedding
            topics: Topic label for each embedding
            
        Returns:
            Dictionary mapping cluster_id to topic distribution
        """
        cluster_topic_dist = defaultdict(lambda: defaultdict(int))
        
        for label, topic in zip(cluster_labels, topics):
            if label != -1:  # Ignore noise points
                cluster_topic_dist[label][topic] += 1
        
        return {k: dict(v) for k, v in cluster_topic_dist.items()}

