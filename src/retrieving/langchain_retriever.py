"""
LangChain BaseRetriever wrapper for Cochrane medical document retrieval.
"""

from typing import List, Optional, Dict, Any
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import ConfigDict
from src.retrieving.retriever import CochraneRetriever, RetrievalResult


class CochraneLangChainRetriever(BaseRetriever):
    """
    LangChain-compatible retriever for Cochrane medical literature.

    Wraps the CochraneRetriever and returns LangChain Document objects
    with rich medical metadata.
    """

    retriever: CochraneRetriever
    top_k: int = 10
    level_filter: Optional[str] = None
    topic_filter: Optional[str] = None
    quality_filter: Optional[str] = None
    section_filter: Optional[str] = None
    statistical_only: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        top_k: int = 10,
        level: Optional[str] = None,
        topic: Optional[str] = None,
        quality_grade: Optional[str] = None,
        section: Optional[str] = None,
        statistical_only: bool = False,
        **kwargs,
    ):
        """
        Initialize LangChain retriever.

        Args:
            top_k: Maximum number of results to return
            level: Filter by chunk level (DOCUMENT, SECTION, SUBSECTION, PARAGRAPH)
            topic: Filter by medical topic
            quality_grade: Filter by quality grade (A, B, C)
            section: Filter by section name (methods, results, etc.)
            statistical_only: Only return chunks with statistical data
        """
        # Initialize base retriever
        retriever = CochraneRetriever()

        super().__init__(
            retriever=retriever,
            top_k=top_k,
            level_filter=level,
            topic_filter=topic,
            quality_filter=quality_grade,
            section_filter=section,
            statistical_only=statistical_only,
            **kwargs,
        )

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """
        Retrieve relevant documents for the given query.

        Args:
            query: Natural language medical query
            run_manager: Callback manager for the retriever run

        Returns:
            List of LangChain Document objects with medical metadata
        """
        # Use CochraneRetriever to get results
        results = self.retriever.search(
            query=query,
            limit=self.top_k,
            level=self.level_filter,
            topic=self.topic_filter,
            quality_grade=self.quality_filter,
            section=self.section_filter,
            statistical_only=self.statistical_only,
        )

        # Convert to LangChain Documents
        documents = [self._result_to_document(result) for result in results]

        return documents

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Public method to retrieve documents."""
        return self._get_relevant_documents(query)

    def _result_to_document(self, result: RetrievalResult) -> Document:
        """
        Convert RetrievalResult to LangChain Document with metadata.

        Args:
            result: Retrieval result from CochraneRetriever

        Returns:
            LangChain Document with medical metadata
        """
        # Use enriched content if available (Stage 3 hierarchical context)
        # Otherwise, format with title and section context
        if result.enriched_content:
            # Hierarchical context already included in enriched_content
            content = f"Title: {result.title}\n\n{result.enriched_content}"
        else:
            # Fallback: format content with title and section context
            content = f"Title: {result.title}\n"
            content += f"Section: {result.section_name}"
            if result.subsection_name:
                content += f" > {result.subsection_name}"
            content += f"\n\n{result.content}"

        # Build metadata dictionary
        metadata = {
            "chunk_id": result.chunk_id,
            "document_id": result.document_id,
            "level": result.level,
            "title": result.title,
            "url": result.url,
            "doi": result.doi,
            "section_name": result.section_name,
            "subsection_name": result.subsection_name,
            "topic_name": result.topic_name,
            "quality_grade": result.quality_grade,
            "is_statistical": result.is_statistical,
            "distance": result.distance,
            "relevance_score": 1.0 - result.distance,
        }

        return Document(page_content=content, metadata=metadata)

    def get_retriever_with_filters(
        self,
        level: Optional[str] = None,
        topic: Optional[str] = None,
        quality_grade: Optional[str] = None,
        section: Optional[str] = None,
        statistical_only: bool = False,
    ) -> "CochraneLangChainRetriever":
        """
        Create a new retriever instance with different filters.

        Args:
            level: Filter by chunk level
            topic: Filter by medical topic
            quality_grade: Filter by quality grade (A, B, C)
            section: Filter by section name
            statistical_only: Only return statistical chunks

        Returns:
            New retriever instance with updated filters
        """
        return CochraneLangChainRetriever(
            top_k=self.top_k,
            level=level if level is not None else self.level_filter,
            topic=topic if topic is not None else self.topic_filter,
            quality_grade=(
                quality_grade if quality_grade is not None else self.quality_filter
            ),
            section=section if section is not None else self.section_filter,
            statistical_only=statistical_only,
        )

    def close(self):
        """Close underlying retriever connections."""
        if self.retriever:
            self.retriever.close()


class MedicalQueryRetriever(CochraneLangChainRetriever):
    """
    Specialized retriever for medical queries with intelligent defaults.

    Automatically adjusts retrieval strategy based on query intent.
    """

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """
        Retrieve with medical query understanding.

        Analyzes query for:
        - Statistical evidence requests → prioritize statistical chunks
        - Treatment effectiveness → focus on results and conclusions
        - Safety/adverse effects → focus on results and discussion
        - Methodology → focus on methods section
        """
        query_lower = query.lower()

        # Detect statistical queries
        statistical_keywords = [
            "statistical",
            "p-value",
            "confidence interval",
            "effect size",
            "significance",
            "odds ratio",
            "risk ratio",
            "hazard ratio",
        ]
        if any(keyword in query_lower for keyword in statistical_keywords):
            self.statistical_only = True

        # Detect section-specific queries
        if any(
            word in query_lower
            for word in ["method", "methodology", "how study", "search strategy"]
        ):
            self.section_filter = "methods"
        elif any(
            word in query_lower
            for word in ["result", "finding", "outcome", "effectiveness"]
        ):
            self.section_filter = "results"
        elif any(
            word in query_lower
            for word in ["conclusion", "implication", "recommendation"]
        ):
            self.section_filter = "authors_conclusions"

        # Prioritize high-quality evidence for clinical questions
        clinical_keywords = [
            "treatment",
            "intervention",
            "therapy",
            "effectiveness",
            "efficacy",
        ]
        if any(keyword in query_lower for keyword in clinical_keywords):
            self.quality_filter = "A"  # Only Grade A for clinical questions

        # Use parent method for actual retrieval
        return super()._get_relevant_documents(query, run_manager=run_manager)
