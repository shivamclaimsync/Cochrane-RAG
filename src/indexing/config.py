import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class WeaviateConfig:
    URL = os.getenv('WEAVIATE_URL', '')
    API_KEY = os.getenv('WEAVIATE_API_KEY', '')
    
    COLLECTION_DOCUMENTS = 'CochraneDocument'
    COLLECTION_CHUNKS = 'CochraneChunk'
    COLLECTION_HISTORY = 'ProcessingHistory'
    
    BATCH_SIZE = 100
    TIMEOUT = 30


class ChunkingConfig:
    MIN_PARAGRAPH_LENGTH = 50
    MAX_CHUNK_SIZE = 10000
    
    STATISTICAL_PATTERNS = [
        r'\bp\s*[<>=]\s*0\.\d+',
        r'\b95%\s*CI\b',
        r'\bconfidence interval\b',
        r'\brisk ratio\b',
        r'\bodds ratio\b',
        r'\bmean difference\b'
    ]


class PathConfig:
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    PROCESSED_DATA_DIR = PROJECT_ROOT / 'processed_data'
    LOGS_DIR = PROJECT_ROOT / 'processing_logs'


class EmbeddingConfig:
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'openai')
    
    OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'text-embedding-3-small')
    MEDCPT_QUERY_MODEL = os.getenv('MEDCPT_QUERY_MODEL', 'ncbi/MedCPT-Query-Encoder')
    MEDCPT_ARTICLE_MODEL = os.getenv('MEDCPT_ARTICLE_MODEL', 'ncbi/MedCPT-Article-Encoder')
    BIOLORD_MODEL_NAME = os.getenv('BIOLORD_MODEL_NAME', 'FremyCompany/BioLORD-2023')
    
    DEVICE = os.getenv('EMBEDDING_DEVICE', 'cpu')

