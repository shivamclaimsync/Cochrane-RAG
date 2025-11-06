"""Retrieval module for Cochrane RAG system."""

from src.retrieving.retriever import CochraneRetriever, RetrievalResult
from src.retrieving.query_rewriter import MedicalQueryRewriter, QueryVariant, QueryFusionRetriever
from src.retrieving.multi_query_retriever import MultiQueryRetriever
from src.retrieving.reranker import MedicalReranker, ScoredDocument
from src.retrieving.langchain_retriever import CochraneLangChainRetriever
from src.retrieving.base_embedder import BaseEmbedder
from src.retrieving.embedder import OpenAIEmbedder

def __getattr__(name):
    if name == "MedCPTEmbedder":
        from src.retrieving.medcpt_embedder import MedCPTEmbedder
        return MedCPTEmbedder
    elif name == "BioLORDEmbedder":
        from src.retrieving.biolord_embedder import BioLORDEmbedder
        return BioLORDEmbedder
    elif name == "get_embedder":
        from src.retrieving.embedder_factory import get_embedder
        return get_embedder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "CochraneRetriever",
    "RetrievalResult",
    "MedicalQueryRewriter",
    "QueryVariant",
    "QueryFusionRetriever",
    "MultiQueryRetriever",
    "MedicalReranker",
    "ScoredDocument",
    "CochraneLangChainRetriever",
    "BaseEmbedder",
    "OpenAIEmbedder",
    "MedCPTEmbedder",
    "BioLORDEmbedder",
    "get_embedder",
]

