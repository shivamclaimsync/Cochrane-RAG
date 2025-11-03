"""
Multi-query retrieval system for medical RAG.

Retrieves documents from multiple decomposed sub-queries and merges results
for comprehensive coverage of complex medical questions.
"""

from typing import List, Dict, Set, Optional
from src.retrieving.retriever import CochraneRetriever, RetrievalResult
from src.retrieving.query_decomposer import MedicalQueryDecomposer, SubQuery


class MultiQueryRetriever:
    """
    Retrieve documents from multiple decomposed sub-queries.

    Orchestrates query decomposition, parallel retrieval, and intelligent merging
    to provide comprehensive results for complex medical queries.
    """

    def __init__(
        self,
        decomposer: Optional[MedicalQueryDecomposer] = None,
        retriever: Optional[CochraneRetriever] = None,
        k_per_subquery: int = 5,
        final_k: int = 10,
        max_subqueries: int = 4,
    ):
        """
        Initialize multi-query retriever.

        Args:
            decomposer: Query decomposer instance (creates default if None)
            retriever: Base retriever instance (creates default if None)
            k_per_subquery: Number of results to retrieve per sub-query
            final_k: Final number of results after merging
            max_subqueries: Maximum number of sub-queries to generate
        """
        self.decomposer = decomposer or MedicalQueryDecomposer()
        self.retriever = retriever or CochraneRetriever()
        self.k_per_subquery = k_per_subquery
        self.final_k = final_k
        self.max_subqueries = max_subqueries

    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        Decompose query and retrieve documents from multiple sub-queries.

        Strategy:
        1. Decompose query into focused sub-queries
        2. Retrieve top_k per sub-query
        3. Merge and deduplicate results
        4. Return top K final results

        Args:
            query: User query
            top_k: Maximum number of results to return

        Returns:
            List of merged and deduplicated retrieval results
        """
        # Step 1: Decompose query
        sub_queries = self.decomposer.decompose(query)
        
        # Limit number of sub-queries
        if len(sub_queries) > self.max_subqueries:
            sub_queries = sub_queries[: self.max_subqueries]

        # Log decomposition if multiple sub-queries
        if len(sub_queries) > 1:
            print(f"🔀 Decomposed into {len(sub_queries)} sub-queries:")
            for i, sq in enumerate(sub_queries, 1):
                print(f"   {i}. [{sq.intent}] {sq.text[:80]}...")

        # Step 2: Single sub-query - use standard retrieval
        if len(sub_queries) == 1:
            sq = sub_queries[0]
            results = self.retriever.search(
                query=sq.text,
                limit=top_k,
                statistical_only=sq.statistical_only,
                section=sq.section_hint,
            )
            # Tag with sub-query metadata
            for result in results:
                result.sub_query_intent = sq.intent
                result.sub_query_priority = sq.priority
            return results

        # Step 3: Multiple sub-queries - retrieve for each
        all_results = []
        for sub_query in sub_queries:
            try:
                # Retrieve with sub-query specific settings
                results = self.retriever.search(
                    query=sub_query.text,
                    limit=self.k_per_subquery,
                    statistical_only=sub_query.statistical_only,
                    section=sub_query.section_hint,
                )

                # Tag results with sub-query metadata
                for result in results:
                    result.sub_query_intent = sub_query.intent
                    result.sub_query_priority = sub_query.priority

                all_results.extend(results)

            except Exception as e:
                print(f"⚠️ Error retrieving for sub-query '{sub_query.text[:50]}...': {e}")
                continue

        if not all_results:
            print("⚠️ No results retrieved from any sub-queries")
            return []

        # Step 4: Merge and deduplicate
        merged_results = self._merge_and_deduplicate(all_results)

        # Step 5: Sort by relevance with diversity consideration
        sorted_results = self._sort_by_relevance_and_diversity(merged_results)

        # Step 6: Return top K
        final_results = sorted_results[:top_k]
        print(f"✅ Retrieved {len(final_results)} results from {len(sub_queries)} sub-queries")
        return final_results

    def _merge_and_deduplicate(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Merge results from multiple sub-queries and remove duplicates.

        When duplicate chunks are found, keep the result with the best (lowest) distance score.

        Args:
            results: List of retrieval results

        Returns:
            Deduplicated list of results
        """
        seen: Dict[str, RetrievalResult] = {}  # chunk_id -> best result

        for result in results:
            if result.chunk_id in seen:
                existing = seen[result.chunk_id]
                # Keep result with better distance score (lower is better)
                if result.distance < existing.distance:
                    seen[result.chunk_id] = result
                # If distances are similar, preserve intent metadata from higher priority
                elif (
                    abs(result.distance - existing.distance) < 0.05
                    and hasattr(result, "sub_query_priority")
                    and hasattr(existing, "sub_query_priority")
                    and result.sub_query_priority < existing.sub_query_priority
                ):
                    seen[result.chunk_id] = result
            else:
                seen[result.chunk_id] = result

        return list(seen.values())

    def _sort_by_relevance_and_diversity(
        self, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Sort results to maximize both relevance and diversity.

        Strategy:
        - Primary sort: by distance (relevance)
        - Secondary goal: ensure representation from different sub-queries
        - Balance between relevance and coverage

        Args:
            results: List of retrieval results

        Returns:
            Sorted list of results
        """
        # Group results by sub-query intent to track diversity
        intent_groups: Dict[str, List[RetrievalResult]] = {}
        for result in results:
            intent = getattr(result, "sub_query_intent", "general")
            if intent not in intent_groups:
                intent_groups[intent] = []
            intent_groups[intent].append(result)

        # Sort each group by distance
        for intent in intent_groups:
            intent_groups[intent].sort(key=lambda r: r.distance)

        # If only one intent, just sort by distance
        if len(intent_groups) == 1:
            return list(intent_groups.values())[0]

        # Multiple intents - create diverse ordering
        # Strategy: interleave results from different intents
        merged = []
        max_len = max(len(group) for group in intent_groups.values())

        for i in range(max_len):
            # Take one result from each intent group at position i
            # Sorted by distance ensures we get best results first
            for intent in sorted(intent_groups.keys()):  # Stable sort for reproducibility
                if i < len(intent_groups[intent]):
                    merged.append(intent_groups[intent][i])

        # Remove duplicates while preserving order (safety check)
        seen: Set[str] = set()
        unique = []
        for result in merged:
            if result.chunk_id not in seen:
                seen.add(result.chunk_id)
                unique.append(result)

        return unique

    def close(self):
        """Close underlying retriever connections."""
        if self.retriever:
            self.retriever.close()

