from typing import List
import os
from src.retrieving.base_embedder import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            print(f"✅ OpenAI Embedder ready ({model_name})")
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    def encode(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(model=self.model_name, input=text)
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(model=self.model_name, input=texts)
            return [item.embedding for item in response.data]
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def get_dimension(self) -> int:
        if "large" in self.model_name:
            return 3072
        return 1536
    
    def get_model_name(self) -> str:
        return f"OpenAI ({self.model_name})"
