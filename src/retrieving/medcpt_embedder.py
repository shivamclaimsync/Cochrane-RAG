from typing import List
import torch
from sentence_transformers import SentenceTransformer
from src.retrieving.base_embedder import BaseEmbedder


class MedCPTEmbedder(BaseEmbedder):
    
    def __init__(
        self,
        query_model: str = "ncbi/MedCPT-Query-Encoder",
        article_model: str = "ncbi/MedCPT-Article-Encoder",
        device: str = None
    ):
        self.query_model_name = query_model
        self.article_model_name = article_model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        self.query_encoder = SentenceTransformer(query_model, device=self.device)
        self.article_encoder = SentenceTransformer(article_model, device=self.device)
        self.current_mode = "article"
        
        print(f"✅ MedCPT Embedder ready (device: {self.device})")
    
    def set_mode(self, mode: str):
        if mode not in ["query", "article"]:
            raise ValueError("Mode must be 'query' or 'article'")
        self.current_mode = mode
    
    def encode(self, text: str) -> List[float]:
        encoder = self.query_encoder if self.current_mode == "query" else self.article_encoder
        embedding = encoder.encode(text, convert_to_tensor=False, show_progress_bar=False)
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        encoder = self.query_encoder if self.current_mode == "query" else self.article_encoder
        embeddings = encoder.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        return 768
    
    def get_model_name(self) -> str:
        return f"MedCPT (query: {self.query_model_name}, article: {self.article_model_name})"

