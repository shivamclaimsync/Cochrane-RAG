"""
Cross-encoder re-ranker for precise medical relevance scoring.

Uses HuggingFace Inference API for cross-encoder models.
Falls back gracefully if API key is not available.
"""

from typing import List, Dict, Any, Optional, Tuple
import warnings
import os
import requests


class CrossEncoderReranker:
    """
    Cross-encoder re-ranker for final-stage medical document scoring.

    Uses HuggingFace Inference API to score query-document pairs
    for more accurate relevance than bi-encoders.

    Requires: HUGGINGFACE_API_KEY environment variable
    Falls back to distance-based scoring if not available.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2",
    ):
        """
        Initialize cross-encoder re-ranker with HuggingFace API.

        Args:
            model_name: HuggingFace cross-encoder model identifier
        """
        self.model_name = model_name
        self.available = False
        self.api_key = None
        self.api_url = None
        self.headers = None

        self._init_hf_api()

    def _init_hf_api(self):
        """Initialize HuggingFace Inference API for cross-encoder scoring."""
        try:
            self.api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not self.api_key:
                warnings.warn(
                    "HUGGINGFACE_API_KEY not set. Cross-encoder disabled. "
                    "Set HUGGINGFACE_API_KEY in environment to enable."
                )
                self.available = False
                return

            self.api_url = (
                f"https://api-inference.huggingface.co/models/{self.model_name}"
            )
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
            self.available = True
            print(f"✅ Cross-encoder reranker ready (HuggingFace API): {self.model_name}")

        except Exception as e:
            warnings.warn(f"Could not initialize HuggingFace API cross-encoder: {e}")
            self.available = False

    def rerank(
        self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Re-rank documents using HuggingFace cross-encoder scoring.

        Args:
            query: Query text
            documents: List of documents to re-rank
            top_k: Return only top K documents

        Returns:
            List of (document, score) tuples, sorted by score
        """
        if not self.available:
            return self._fallback_rerank(documents, top_k)

        return self._rerank_hf_api(query, documents, top_k)

    def _rerank_hf_api(
        self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Re-rank using HuggingFace Inference API."""
        scored_docs = []

        for doc in documents:
            content = doc.get("page_content", "")

            # Truncate very long documents
            if len(content) > 2000:
                content = content[:2000]

            try:
                # Cross-encoder scoring via HF API
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "inputs": {"source_sentence": query, "sentences": [content]},
                        "options": {"wait_for_model": True},
                    },
                    timeout=10,
                )

                if response.status_code == 200:
                    scores = response.json()
                    score = scores[0] if isinstance(scores, list) else 0.5
                else:
                    # Fallback to metadata score
                    score = doc.get("metadata", {}).get("relevance_score", 0.5)

                scored_docs.append((doc, float(score)))

            except Exception as e:
                warnings.warn(f"Cross-encoder API error: {e}")
                # Use fallback score
                score = doc.get("metadata", {}).get("relevance_score", 0.5)
                scored_docs.append((doc, float(score)))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        if top_k:
            return scored_docs[:top_k]

        return scored_docs

    def _fallback_rerank(
        self, documents: List[Dict[str, Any]], top_k: Optional[int]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Fallback re-ranking using existing relevance scores.

        Used when cross-encoder is not available.
        """
        scored_docs = []

        for doc in documents:
            # Use existing relevance score from metadata
            metadata = doc.get("metadata", {})
            score = metadata.get("relevance_score", 0.5)

            # Boost by quality grade if available
            quality_grade = metadata.get("quality_grade", "").upper()
            quality_boost = {"A": 0.1, "B": 0.05, "C": 0.0}.get(quality_grade, 0.0)

            final_score = min(1.0, score + quality_boost)
            scored_docs.append((doc, final_score))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        if top_k:
            return scored_docs[:top_k]

        return scored_docs

    def compress_documents(self, documents: List[Any], query: str) -> List[Any]:
        """
        LangChain-compatible document compression interface.

        Args:
            documents: List of LangChain Documents
            query: Query string

        Returns:
            Re-ranked documents with updated scores
        """
        # Convert to dict format
        doc_dicts = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in documents
        ]

        # Re-rank
        scored_docs = self.rerank(query, doc_dicts, top_k=len(documents))

        # Convert back to LangChain Documents
        from langchain_core.documents import Document

        reranked_documents = []
        for doc_dict, score in scored_docs:
            metadata = doc_dict["metadata"].copy()
            metadata["cross_encoder_score"] = float(score)

            doc = Document(page_content=doc_dict["page_content"], metadata=metadata)
            reranked_documents.append(doc)

        return reranked_documents


class HybridReranker:
    """
    Combines custom medical reranker with cross-encoder for best results.

    Strategy:
    1. Medical reranker filters to top-20 using domain-specific signals
    2. Cross-encoder refines to top-10 using deep semantic understanding
    """

    def __init__(
        self,
        medical_reranker=None,
        cross_encoder_reranker=None,
        stage1_top_k: int = 20,
        stage2_top_k: int = 10,
    ):
        """
        Initialize hybrid re-ranker.

        Args:
            medical_reranker: MedicalReranker instance
            cross_encoder_reranker: CrossEncoderReranker instance
            stage1_top_k: Documents to pass to stage 2
            stage2_top_k: Final documents to return
        """
        from src.retrieving.reranker import MedicalReranker

        self.medical_reranker = medical_reranker or MedicalReranker()
        self.cross_encoder = cross_encoder_reranker or CrossEncoderReranker()
        self.stage1_top_k = stage1_top_k
        self.stage2_top_k = stage2_top_k

    def rerank(
        self, query: str, documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Two-stage hybrid re-ranking.

        Args:
            query: Query text
            documents: Documents to re-rank

        Returns:
            Re-ranked documents
        """
        # Stage 1: Medical re-ranker
        stage1_docs = self.medical_reranker.rerank(
            documents, query, top_k=self.stage1_top_k
        )

        # Convert to dict format for cross-encoder
        stage1_dicts = [
            {"page_content": doc.content, "metadata": doc.metadata}
            for doc in stage1_docs
        ]

        # Stage 2: Cross-encoder re-ranking
        if self.cross_encoder.available:
            stage2_results = self.cross_encoder.rerank(
                query, stage1_dicts, top_k=self.stage2_top_k
            )

            # Extract just the documents
            final_docs = [doc for doc, score in stage2_results]
        else:
            # Cross-encoder not available, use medical reranker results
            final_docs = stage1_dicts[: self.stage2_top_k]

        return final_docs
