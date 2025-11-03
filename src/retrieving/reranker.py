"""
Custom medical re-ranker for Cochrane systematic reviews.

Implements multi-factor scoring based on:
- Quality grade (A > B > C)
- Statistical relevance
- Section relevance
- Base semantic similarity
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class ScoredDocument:
    """Document with re-ranking score."""

    content: str
    metadata: Dict[str, Any]
    base_score: float
    rerank_score: float
    score_breakdown: Dict[str, float]


class MedicalReranker:
    """
    Custom re-ranker for medical literature based on multiple factors.

    Scoring Weights:
    - Quality Score (30%): Grade A=1.0, B=0.7, C=0.4
    - Statistical Relevance (20%): Boost for statistical content when relevant
    - Section Relevance (20%): Match query intent to section
    - Base Semantic Score (30%): From initial retrieval distance
    """

    # Scoring weights
    WEIGHT_QUALITY = 0.30
    WEIGHT_STATISTICAL = 0.20
    WEIGHT_SECTION = 0.20
    WEIGHT_SEMANTIC = 0.30

    # Quality grade values
    QUALITY_SCORES = {
        "A": 1.0,  # High quality
        "B": 0.7,  # Moderate quality
        "C": 0.4,  # Lower quality
        "": 0.5,  # Unknown quality
    }

    # Section relevance for different query types
    SECTION_PRIORITIES = {
        "effectiveness": ["results", "authors_conclusions", "main_results"],
        "safety": ["results", "discussion", "adverse_effects"],
        "methodology": ["methods", "search_methods", "data_collection"],
        "statistical": ["results", "statistical_analysis"],
        "conclusion": ["authors_conclusions", "discussion"],
        "background": ["background", "abstract"],
        "general": ["abstract", "main_results", "authors_conclusions"],
    }

    def __init__(
        self,
        weight_quality: float = WEIGHT_QUALITY,
        weight_statistical: float = WEIGHT_STATISTICAL,
        weight_section: float = WEIGHT_SECTION,
        weight_semantic: float = WEIGHT_SEMANTIC,
    ):
        """
        Initialize medical re-ranker with custom weights.

        Args:
            weight_quality: Weight for quality grade scoring
            weight_statistical: Weight for statistical relevance
            weight_section: Weight for section relevance
            weight_semantic: Weight for base semantic similarity
        """
        self.weight_quality = weight_quality
        self.weight_statistical = weight_statistical
        self.weight_section = weight_section
        self.weight_semantic = weight_semantic

        # Normalize weights to sum to 1.0
        total = weight_quality + weight_statistical + weight_section + weight_semantic
        self.weight_quality /= total
        self.weight_statistical /= total
        self.weight_section /= total
        self.weight_semantic /= total

    def rerank(
        self, documents: List[Dict[str, Any]], query: str, top_k: Optional[int] = None
    ) -> List[ScoredDocument]:
        """
        Re-rank documents based on medical relevance factors.

        Args:
            documents: List of documents with metadata
            query: Original query for context
            top_k: Return only top K documents (None = all)

        Returns:
            List of scored documents sorted by rerank_score
        """
        # Detect query intent
        query_intent = self._detect_query_intent(query)
        is_statistical_query = self._is_statistical_query(query)

        # Score each document
        scored_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})

            # Calculate component scores
            quality_score = self._score_quality(metadata)
            statistical_score = self._score_statistical_relevance(
                metadata, is_statistical_query
            )
            section_score = self._score_section_relevance(metadata, query_intent)
            semantic_score = metadata.get("relevance_score", 0.5)  # From retrieval

            # Calculate weighted final score
            rerank_score = (
                quality_score * self.weight_quality
                + statistical_score * self.weight_statistical
                + section_score * self.weight_section
                + semantic_score * self.weight_semantic
            )

            # Store breakdown for transparency
            score_breakdown = {
                "quality": quality_score,
                "statistical": statistical_score,
                "section": section_score,
                "semantic": semantic_score,
                "final": rerank_score,
            }

            scored_doc = ScoredDocument(
                content=doc.get("page_content", ""),
                metadata=metadata,
                base_score=semantic_score,
                rerank_score=rerank_score,
                score_breakdown=score_breakdown,
            )
            scored_docs.append(scored_doc)

        # Sort by rerank score (descending)
        scored_docs.sort(key=lambda x: x.rerank_score, reverse=True)

        # Return top K if specified
        if top_k:
            return scored_docs[:top_k]

        return scored_docs

    def _score_quality(self, metadata: Dict[str, Any]) -> float:
        """
        Score based on Cochrane quality grade.

        Args:
            metadata: Document metadata

        Returns:
            Quality score (0.0-1.0)
        """
        quality_grade = metadata.get("quality_grade", "").upper()
        return self.QUALITY_SCORES.get(quality_grade, 0.5)

    def _score_statistical_relevance(
        self, metadata: Dict[str, Any], is_statistical_query: bool
    ) -> float:
        """
        Score based on statistical content relevance.

        Args:
            metadata: Document metadata
            is_statistical_query: Whether query seeks statistical evidence

        Returns:
            Statistical relevance score (0.0-1.0)
        """
        has_statistical = metadata.get("is_statistical", False)

        if is_statistical_query:
            # High score if document has stats and query wants stats
            return 1.0 if has_statistical else 0.3
        else:
            # Neutral score if query doesn't specifically want stats
            return 0.6 if has_statistical else 0.5

    def _score_section_relevance(
        self, metadata: Dict[str, Any], query_intent: str
    ) -> float:
        """
        Score based on section relevance to query intent.

        Args:
            metadata: Document metadata
            query_intent: Detected query intent

        Returns:
            Section relevance score (0.0-1.0)
        """
        section = metadata.get("section_name", "").lower()

        # Get relevant sections for this query intent
        relevant_sections = self.SECTION_PRIORITIES.get(
            query_intent, self.SECTION_PRIORITIES["general"]
        )

        # Check if section matches priority list
        for idx, priority_section in enumerate(relevant_sections):
            if priority_section in section:
                # Higher score for higher priority sections
                return 1.0 - (idx * 0.15)  # Decreases: 1.0, 0.85, 0.70, ...

        # Default score for non-matching sections
        return 0.4

    def _detect_query_intent(self, query: str) -> str:
        """
        Detect the intent of the medical query.

        Args:
            query: User query

        Returns:
            Query intent category
        """
        query_lower = query.lower()

        # Effectiveness/treatment queries
        if any(
            word in query_lower
            for word in [
                "effective",
                "efficacy",
                "treatment",
                "therapy",
                "intervention",
                "benefit",
            ]
        ):
            return "effectiveness"

        # Safety/adverse effect queries
        if any(
            word in query_lower
            for word in [
                "safety",
                "safe",
                "adverse",
                "side effect",
                "harm",
                "risk",
                "toxicity",
            ]
        ):
            return "safety"

        # Methodology queries
        if any(
            word in query_lower
            for word in [
                "method",
                "how",
                "design",
                "study design",
                "search strategy",
                "criteria",
            ]
        ):
            return "methodology"

        # Statistical evidence queries
        if any(
            word in query_lower
            for word in [
                "statistical",
                "p-value",
                "confidence",
                "significance",
                "evidence",
            ]
        ):
            return "statistical"

        # Conclusion/recommendation queries
        if any(
            word in query_lower
            for word in [
                "conclusion",
                "recommend",
                "implication",
                "should",
                "guideline",
            ]
        ):
            return "conclusion"

        # Background/overview queries
        if any(
            word in query_lower
            for word in ["what is", "overview", "background", "about", "define"]
        ):
            return "background"

        # Default to general
        return "general"

    def _is_statistical_query(self, query: str) -> bool:
        """
        Determine if query is seeking statistical evidence.

        Args:
            query: User query

        Returns:
            True if statistical query
        """
        statistical_keywords = [
            "statistical",
            "statistically",
            "p-value",
            "p value",
            "confidence interval",
            "ci",
            "significance",
            "significant",
            "odds ratio",
            "or",
            "risk ratio",
            "rr",
            "hazard ratio",
            "hr",
            "effect size",
            "mean difference",
            "standardized mean difference",
            "meta-analysis",
            "pooled",
            "heterogeneity",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in statistical_keywords)


class ContextualCompressionReranker:
    """
    LangChain-compatible document compressor for medical re-ranking.

    Can be used with ContextualCompressionRetriever.
    """

    def __init__(self, reranker: Optional[MedicalReranker] = None, top_k: int = 10):
        """
        Initialize compression re-ranker.

        Args:
            reranker: Medical re-ranker instance (creates default if None)
            top_k: Number of documents to return after re-ranking
        """
        self.reranker = reranker or MedicalReranker()
        self.top_k = top_k

    def compress_documents(self, documents: List[Any], query: str) -> List[Any]:
        """
        Compress and re-rank documents for LangChain.

        Args:
            documents: List of LangChain Documents
            query: Query string

        Returns:
            Re-ranked and filtered documents
        """
        # Convert to dict format for reranker
        doc_dicts = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in documents
        ]

        # Re-rank
        scored_docs = self.reranker.rerank(doc_dicts, query, top_k=self.top_k)

        # Convert back to LangChain Documents
        from langchain_core.documents import Document

        reranked_documents = []
        for scored_doc in scored_docs:
            # Add score breakdown to metadata
            metadata = scored_doc.metadata.copy()
            metadata["rerank_score"] = scored_doc.rerank_score
            metadata["score_breakdown"] = scored_doc.score_breakdown

            doc = Document(page_content=scored_doc.content, metadata=metadata)
            reranked_documents.append(doc)

        return reranked_documents
