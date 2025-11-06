from src.retrieving.base_embedder import BaseEmbedder
from src.indexing.config import EmbeddingConfig


def get_embedder(config: EmbeddingConfig = None, mode: str = "article") -> BaseEmbedder:
    if config is None:
        config = EmbeddingConfig()
    
    model_type = config.EMBEDDING_MODEL.lower()
    
    if model_type == "openai":
        from src.retrieving.embedder import OpenAIEmbedder
        return OpenAIEmbedder(model_name=config.OPENAI_MODEL_NAME)
    
    elif model_type == "medcpt":
        from src.retrieving.medcpt_embedder import MedCPTEmbedder
        embedder = MedCPTEmbedder(
            query_model=config.MEDCPT_QUERY_MODEL,
            article_model=config.MEDCPT_ARTICLE_MODEL,
            device=config.DEVICE
        )
        embedder.set_mode(mode)
        return embedder
    
    elif model_type == "biolord":
        from src.retrieving.biolord_embedder import BioLORDEmbedder
        return BioLORDEmbedder(
            model_name=config.BIOLORD_MODEL_NAME,
            device=config.DEVICE
        )
    
    else:
        raise ValueError(
            f"Unknown embedding model: {model_type}. "
            f"Choose from: openai, medcpt, biolord"
        )

