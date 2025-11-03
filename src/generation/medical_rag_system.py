"""
Main user-facing medical RAG system.
"""

from typing import Dict, List, Optional, Union

from src.generation.llm import MedicalLLM
from src.generation.rag_chain import MedicalRAGChain
from src.retrieving.langchain_retriever import CochraneLangChainRetriever
from src.retrieving.reranker import MedicalReranker


class CochraneMedicalRAG:
    """Evidence-based medical Q&A system using Cochrane reviews."""

    def __init__(
        self,
        model: Optional[str] = None,
        use_reranker: bool = True,
        top_k: int = 10,
        verbose: bool = True,
    ):
        """
        Initialize medical RAG system.

        Args:
            model: OpenAI model name (default: gpt-4-turbo-preview)
            use_reranker: Enable medical re-ranking
            top_k: Number of documents to retrieve
            verbose: Print initialization info
        """
        if verbose:
            print("Initializing Cochrane Medical RAG System...")

        self.llm = MedicalLLM(model_name=model)

        retriever = CochraneLangChainRetriever(top_k=top_k)
        reranker = MedicalReranker() if use_reranker else None

        self.chain = MedicalRAGChain(
            llm=self.llm, retriever=retriever, reranker=reranker, top_k=top_k
        )

        self.retriever = retriever
        self.verbose = verbose

        if verbose:
            print("✅ RAG System ready")

    def ask(self, question: str, format: str = "string") -> Union[str, Dict]:
        """
        Ask a medical question and get evidence-based answer.

        Args:
            question: Medical question
            format: Output format ('string' or 'dict')

        Returns:
            Formatted response based on format parameter
        """
        if self.verbose:
            print(f"\n🔍 Question: {question}")

        result = self.chain.invoke(question)

        if self.verbose:
            print(f"✅ Generated response from {result['num_sources']} sources")

        if format == "dict":
            return result

        return self._format_as_string(result)

    def search(
        self, query: str, filters: Optional[Dict] = None, top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for relevant documents without LLM generation.

        Args:
            query: Search query
            filters: Optional filters (level, topic, quality_grade, section, statistical_only)
            top_k: Number of results

        Returns:
            List of relevant documents with metadata
        """
        if filters:
            retriever = self.retriever.get_retriever_with_filters(**filters)
        else:
            retriever = self.retriever

        limit = top_k or retriever.top_k
        documents = retriever.get_relevant_documents(query)

        results = []
        for doc in documents[:limit]:
            metadata = doc.metadata
            results.append(
                {
                    "content": doc.page_content,
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

        return results

    def get_stats(self) -> Dict:
        """Get system statistics."""
        from src.indexing.weaviate_client import WeaviateManager

        weaviate_manager = WeaviateManager()
        stats = weaviate_manager.get_processing_stats()
        weaviate_manager.close()

        return {
            "total_chunks": stats.get("total_chunks", 0),
            "total_documents": stats.get("total_documents", 0),
            "total_documents_processed": stats.get("total_documents_processed", 0),
            "chunks_by_level": stats.get("chunks_by_level", {}),
            "model": self.llm.model_name,
            "reranker_enabled": self.chain.reranker is not None,
        }

    def _format_as_string(self, result: Dict) -> str:
        """Format response dictionary as readable string."""
        lines = []
        lines.append("=" * 80)
        lines.append("EVIDENCE-BASED ANSWER")
        lines.append("=" * 80)
        lines.append(f"\n{result['answer']}\n")
        lines.append("-" * 80)
        lines.append("REFERENCES")
        lines.append("-" * 80)

        for source in result["sources"]:
            url = source.get("url", "")
            if url:
                lines.append(f"{source['index']} - {url}")
            else:
                lines.append(f"{source['index']} - {source.get('title', 'Unknown')}")

        lines.append("")
        lines.append(f"Quality: {result['quality_summary']}")
        lines.append(f"Statistical Evidence: {result['statistical_summary']}")
        lines.append(f"Sources Used: {result['num_sources']}")

        lines.append("=" * 80)

        return "\n".join(lines)

    def close(self):
        """Close connections and cleanup resources."""
        if hasattr(self.retriever, "close"):
            self.retriever.close()
        if self.verbose:
            print("✅ System closed")


