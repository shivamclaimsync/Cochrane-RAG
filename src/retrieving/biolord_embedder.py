from typing import List
import torch
from sentence_transformers import SentenceTransformer
from src.retrieving.base_embedder import BaseEmbedder


class BioLORDEmbedder(BaseEmbedder):
    
    def __init__(
        self,
        model_name: str = "FremyCompany/BioLORD-2023",
        device: str = None
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SentenceTransformer(model_name, device=self.device)
        
        print(f"✅ BioLORD Embedder ready (device: {self.device})")
    
    def encode(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_tensor=False, show_progress_bar=False)
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_name(self) -> str:
        return f"BioLORD ({self.model_name})"

