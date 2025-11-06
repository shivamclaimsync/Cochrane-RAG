from abc import ABC, abstractmethod
from typing import List


class BaseEmbedder(ABC):
    
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass

