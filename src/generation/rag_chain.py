"""
Core RAG chain orchestrating retrieval and generation.
"""

from typing import Dict, List, Optional

from langchain_core.documents import Document

from src.generation.llm import MedicalLLM
from src.generation.prompts import MedicalPromptBuilder
from src.retrieving.langchain_retriever import CochraneLangChainRetriever
from src.retrieving.reranker import MedicalReranker
from src.retrieving.multi_query_retriever import MultiQueryRetriever
from src.retrieving.retriever import RetrievalResult


class MedicalRAGChain:
    """Orchestrates retrieval, re-ranking, and generation for medical Q&A."""

    def __init__(
        self,
        llm: MedicalLLM,
        retriever: CochraneLangChainRetriever,
        reranker: Optional[MedicalReranker] = None,
        top_k: int = 10,
    ):
        """
        Initialize RAG chain components.

        Args:
            llm: MedicalLLM instance
            retriever: Cochrane retriever instance
            reranker: Optional medical reranker
            top_k: Number of documents to retrieve
        """
        self.llm = llm
        self.retriever = retriever
        self.reranker = reranker
        self.top_k = top_k
        
        # Initialize multi-query retriever for query decomposition
        self.multi_query_retriever = MultiQueryRetriever()

    def invoke(self, question: str) -> Dict:
        """
        Execute complete RAG pipeline.

        Args:
            question: Medical question

        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Use multi-query retrieval with automatic decomposition
        retrieval_results = self.multi_query_retriever.retrieve(question, top_k=self.top_k)
        
        # Convert RetrievalResult objects to LangChain Documents
        documents = self._retrieval_results_to_documents(retrieval_results)

        if self.reranker:
            doc_dicts = [
                {"page_content": doc.page_content, "metadata": doc.metadata}
                for doc in documents
            ]
            scored_docs = self.reranker.rerank(doc_dicts, question, top_k=self.top_k)
            documents = self._scored_to_documents(scored_docs)

        if not documents:
            return {
                "answer": "No relevant evidence found in the database.",
                "sources": [],
                "quality_summary": "",
                "statistical_summary": "",
                "num_sources": 0,
                "metadata": {},
            }

        context = MedicalPromptBuilder.format_context(documents)
        quality_summary = MedicalPromptBuilder.generate_quality_summary(documents)
        statistical_summary = MedicalPromptBuilder.generate_statistical_summary(
            documents
        )

        prompt = MedicalPromptBuilder.build_qa_prompt(
            question=question,
            context=context,
            quality_summary=quality_summary,
            statistical_summary=statistical_summary,
        )

        answer = self.llm.generate(prompt)

        return self._format_response(answer, documents, quality_summary, statistical_summary)

    def _retrieval_results_to_documents(self, results: List[RetrievalResult]) -> List[Document]:
        """Convert RetrievalResult objects to LangChain Documents."""
        documents = []
        for result in results:
            # Use enriched content if available (hierarchical context)
            content = f"Title: {result.title}\n\n{result.enriched_content or result.content}"
            
            metadata = {
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
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
                "sub_query_intent": getattr(result, 'sub_query_intent', ''),
                "sub_query_priority": getattr(result, 'sub_query_priority', 0),
            }
            documents.append(Document(page_content=content, metadata=metadata))
        return documents

    def _scored_to_documents(self, scored_docs: List) -> List[Document]:
        """Convert scored documents back to LangChain Documents."""
        documents = []
        for doc in scored_docs:
            if hasattr(doc, "content"):
                page_content = doc.content
                metadata = doc.metadata
            else:
                page_content = doc["page_content"]
                metadata = doc["metadata"]
            documents.append(Document(page_content=page_content, metadata=metadata))
        return documents

    def _format_response(
        self,
        answer: str,
        documents: List[Document],
        quality_summary: str,
        statistical_summary: str,
    ) -> Dict:
        """Format LLM response with metadata and sources."""
        sources = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            sources.append(
                {
                    "index": i,
                    "title": metadata.get("title", "Unknown"),
                    "url": metadata.get("url", ""),
                    "doi": metadata.get("doi", ""),
                    "section": metadata.get("section_name", ""),
                    "topic": metadata.get("topic_name", ""),
                    "quality_grade": metadata.get("quality_grade", ""),
                    "is_statistical": metadata.get("is_statistical", False),
                    "relevance_score": metadata.get("relevance_score", 0.0),
                }
            )

        return {
            "answer": answer,
            "sources": sources,
            "quality_summary": quality_summary,
            "statistical_summary": statistical_summary,
            "num_sources": len(sources),
            "metadata": {
                "model": self.llm.model_name,
                "top_k": self.top_k,
                "reranker_used": self.reranker is not None,
            },
        }

