"""
Multi-query retrieval system for medical RAG using query rewriting and fusion.

Retrieves documents from multiple rewritten query variants and merges results
using Reciprocal Rank Fusion (RRF) for comprehensive coverage.
"""

from typing import List, Dict, Set, Optional
from src.retrieving.retriever import CochraneRetriever, RetrievalResult
from src.retrieving.query_rewriter import MedicalQueryRewriter, QueryFusionRetriever


class MultiQueryRetriever:
    """
    Retrieve documents from multiple rewritten query variants with result fusion.

    Uses query rewriting (synonyms, LLM reformulation, HyDE) to generate variants,
    then fuses results using Reciprocal Rank Fusion for better coverage.
    """

    def __init__(
        self,
        rewriter: Optional[MedicalQueryRewriter] = None,
        retriever: Optional[CochraneRetriever] = None,
        k_per_variant: int = 10,
        final_k: int = 10,
        rrf_k: int = 60,
    ):
        """
        Initialize multi-query retriever with query rewriting.

        Args:
            rewriter: Query rewriter instance (creates default if None)
            retriever: Base retriever instance (creates default if None)
            k_per_variant: Number of results to retrieve per query variant
            final_k: Final number of results after fusion
            rrf_k: RRF constant for reciprocal rank fusion
        """
        self.retriever = retriever or CochraneRetriever()
        self.rewriter = rewriter or MedicalQueryRewriter()
        self.fusion_retriever = QueryFusionRetriever(
            base_retriever=self.retriever,
            rewriter=self.rewriter,
            k_per_variant=k_per_variant,
            final_k=final_k,
            rrf_k=rrf_k,
        )

    def retrieve(self, query: str, top_k: int = 10, **search_kwargs) -> List[RetrievalResult]:
        """
        Rewrite query and retrieve documents using result fusion.

        Strategy:
        1. Rewrite query into multiple variants (synonyms, LLM, HyDE)
        2. Retrieve documents for each variant
        3. Fuse results using Reciprocal Rank Fusion (RRF)
        4. Return top K final results

        Args:
            query: User query
            top_k: Maximum number of results to return
            **search_kwargs: Additional arguments passed to retriever

        Returns:
            List of fused retrieval results
        """
        print(f"🔍 Multi-query retrieval with rewriting and fusion")
        
        # Use the fusion retriever which handles everything
        results = self.fusion_retriever.retrieve(
            query=query,
            top_k=top_k,
            **search_kwargs
        )
        
        return results


    def close(self):
        """Close underlying retriever connections."""
        if self.fusion_retriever:
            self.fusion_retriever.close()

