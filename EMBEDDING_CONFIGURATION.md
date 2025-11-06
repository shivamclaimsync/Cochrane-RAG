# Embedding Model Configuration

This system supports three medical embedding models that can be configured via environment variables.

## Supported Models

### 1. OpenAI (Default)
- Model: `text-embedding-3-small` or `text-embedding-3-large`
- Dimensions: 1536 (small) / 3072 (large)
- Requires: OpenAI API key
- Best for: General medical queries, cloud-based

### 2. MedCPT
- Model: `ncbi/MedCPT-Query-Encoder` and `ncbi/MedCPT-Article-Encoder`
- Dimensions: 768
- Requires: sentence-transformers, torch
- Best for: Medical information retrieval, local deployment

### 3. BioLORD
- Model: `FremyCompany/BioLORD-2023`
- Dimensions: 768
- Requires: sentence-transformers, torch
- Best for: Medical entity understanding, local deployment

## Configuration

Add to your `.env` file:

```bash
# Select embedding model: openai, medcpt, or biolord
EMBEDDING_MODEL=medcpt

# OpenAI settings (if using openai)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL_NAME=text-embedding-3-small

# MedCPT settings (if using medcpt)
MEDCPT_QUERY_MODEL=ncbi/MedCPT-Query-Encoder
MEDCPT_ARTICLE_MODEL=ncbi/MedCPT-Article-Encoder

# BioLORD settings (if using biolord)
BIOLORD_MODEL_NAME=FremyCompany/BioLORD-2023

# Device for local models (cpu or cuda)
EMBEDDING_DEVICE=cpu
```

## Usage Examples

### Using Default Configuration
```python
from src.retrieving import CochraneRetriever

retriever = CochraneRetriever()
results = retriever.search("What are the effects of aspirin?")
```

### Using Specific Embedder
```python
from src.retrieving import get_embedder, CochraneRetriever
from src.indexing.config import EmbeddingConfig

config = EmbeddingConfig()
embedder = get_embedder(config, mode="query")
retriever = CochraneRetriever(embedder=embedder)
```

### Indexing with Specific Model
```python
from src.indexing import IndexingPipeline

pipeline = IndexingPipeline()
pipeline.index_processed_documents(processed_dir)
```

## Important Notes

1. **Re-indexing Required**: When switching embedding models, you must clear the vector store and re-index all documents:
   ```bash
   python run_indexing.py
   ```

2. **Dimension Mismatch**: OpenAI (1536 dims) and MedCPT/BioLORD (768 dims) are not compatible. Clear database before switching.

3. **First Run**: Local models (MedCPT, BioLORD) will download ~400MB on first use.

4. **Performance**: Local models are slower but free. OpenAI is faster but has API costs.

5. **MedCPT Mode**: MedCPT uses different encoders for queries and articles. The system handles this automatically.

## Dependencies

Install required packages:

```bash
# For OpenAI
pip install openai

# For MedCPT and BioLORD
pip install sentence-transformers torch
```

