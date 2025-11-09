"""
Dimensionality reduction using UMAP for embedding visualization.
"""

from typing import Tuple, Optional
import numpy as np
from sklearn.preprocessing import StandardScaler
import umap


class DimensionReducer:
    """Reduces high-dimensional embeddings to 2D/3D using UMAP."""
    
    def __init__(
        self,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        metric: str = 'cosine',
        random_state: int = 42
    ):
        """
        Initialize the dimension reducer.
        
        Args:
            n_neighbors: Number of neighbors for UMAP
            min_dist: Minimum distance parameter for UMAP
            metric: Distance metric for UMAP
            random_state: Random seed for reproducibility
        """
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist
        self.metric = metric
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.reducer_2d = None
        self.reducer_3d = None
    
    def reduce_to_2d(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Reduce embeddings to 2D using UMAP.
        
        Args:
            embeddings: High-dimensional embeddings array (n_samples, n_features)
            
        Returns:
            2D embeddings array (n_samples, 2)
        """
        print("🔄 Reducing to 2D with UMAP...")
        
        # Standardize embeddings
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        # Create and fit 2D reducer
        self.reducer_2d = umap.UMAP(
            n_components=2,
            random_state=self.random_state,
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            metric=self.metric
        )
        umap_2d = self.reducer_2d.fit_transform(embeddings_scaled)
        
        print(f"✅ 2D reduction complete (shape: {umap_2d.shape})")
        return umap_2d
    
    def reduce_to_3d(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Reduce embeddings to 3D using UMAP.
        
        Args:
            embeddings: High-dimensional embeddings array (n_samples, n_features)
            
        Returns:
            3D embeddings array (n_samples, 3)
        """
        print("🔄 Reducing to 3D with UMAP...")
        
        # Standardize embeddings
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        # Create and fit 3D reducer
        self.reducer_3d = umap.UMAP(
            n_components=3,
            random_state=self.random_state,
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            metric=self.metric
        )
        umap_3d = self.reducer_3d.fit_transform(embeddings_scaled)
        
        print(f"✅ 3D reduction complete (shape: {umap_3d.shape})")
        return umap_3d
    
    def reduce_both(self, embeddings: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reduce embeddings to both 2D and 3D.
        
        Args:
            embeddings: High-dimensional embeddings array (n_samples, n_features)
            
        Returns:
            Tuple of (2D embeddings, 3D embeddings)
        """
        print("🔄 Reducing to both 2D and 3D with UMAP...")
        
        # Standardize embeddings once
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        # 2D reduction
        print("   Computing 2D UMAP...")
        self.reducer_2d = umap.UMAP(
            n_components=2,
            random_state=self.random_state,
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            metric=self.metric
        )
        umap_2d = self.reducer_2d.fit_transform(embeddings_scaled)
        
        # 3D reduction
        print("   Computing 3D UMAP...")
        self.reducer_3d = umap.UMAP(
            n_components=3,
            random_state=self.random_state,
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            metric=self.metric
        )
        umap_3d = self.reducer_3d.fit_transform(embeddings_scaled)
        
        print(f"✅ Dimension reduction complete")
        print(f"   2D shape: {umap_2d.shape}, 3D shape: {umap_3d.shape}")
        
        return umap_2d, umap_3d
    
    def transform_2d(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Transform new embeddings to 2D using fitted reducer.
        
        Args:
            embeddings: New embeddings to transform
            
        Returns:
            2D embeddings
        """
        if self.reducer_2d is None:
            raise ValueError("Must call reduce_to_2d() or reduce_both() first")
        
        embeddings_scaled = self.scaler.transform(embeddings)
        return self.reducer_2d.transform(embeddings_scaled)
    
    def transform_3d(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Transform new embeddings to 3D using fitted reducer.
        
        Args:
            embeddings: New embeddings to transform
            
        Returns:
            3D embeddings
        """
        if self.reducer_3d is None:
            raise ValueError("Must call reduce_to_3d() or reduce_both() first")
        
        embeddings_scaled = self.scaler.transform(embeddings)
        return self.reducer_3d.transform(embeddings_scaled)

