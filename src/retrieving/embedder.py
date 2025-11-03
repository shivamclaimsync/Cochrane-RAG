"""
Embedding generation using OpenAI API (replaces HuggingFace for consistency).
"""

from typing import List
import os


class OpenAIEmbedder:
    """Generate embeddings using OpenAI API."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize embedder with OpenAI model.

        Default: text-embedding-3-small (1536-dim, cost-effective)
        Alternatives:
        - text-embedding-3-small (1536-dim, recommended)
        - text-embedding-3-large (3072-dim, higher quality)
        - text-embedding-ada-002 (1536-dim, legacy)
        """
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        # Initialize OpenAI client
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
            print(f"✅ OpenAI Embedder ready ({model_name})")
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )

    def encode(self, text: str) -> List[float]:
        """
        Encode a single text into a vector embedding.

        Args:
            text: Text to encode

        Returns:
            Vector embedding (1536-dim for text-embedding-3-small)
        """
        try:
            response = self.client.embeddings.create(model=self.model_name, input=text)
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(
                f"OpenAI API error: {e}\n"
                f"Model: {self.model_name}\n"
                f"Check your API key and ensure you have credits."
            )

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode multiple texts into vector embeddings.

        Args:
            texts: List of texts to encode

        Returns:
            List of embedding vectors (1536-dim for text-embedding-3-small)
        """
        try:
            response = self.client.embeddings.create(model=self.model_name, input=texts)
            return [item.embedding for item in response.data]
        except Exception as e:
            raise RuntimeError(
                f"OpenAI API error during batch encoding: {e}\n"
                f"Model: {self.model_name}"
            )
