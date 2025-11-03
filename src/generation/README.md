# Generation Module

Evidence-based medical question answering system using Cochrane reviews.

## Quick Start

```python
from src.generation.medical_rag_system import CochraneMedicalRAG

rag = CochraneMedicalRAG()
result = rag.ask("What is the effectiveness of vitamin C for colds?")
print(result)
rag.close()
```

## Command Line

```bash
# Interactive mode
python src/generation/cli.py

# Ask a question
python src/generation/cli.py --question "Is zinc effective for colds?"

# Search without LLM
python src/generation/cli.py --search "asthma corticosteroids"

# Show statistics
python src/generation/cli.py --stats
```

## Demo

```bash
python demo_rag_system.py
```

## Architecture

- **llm.py**: OpenAI LLM wrapper
- **prompts.py**: Medical prompt templates
- **rag_chain.py**: RAG orchestration pipeline
- **medical_rag_system.py**: Main user interface
- **cli.py**: Command-line interface

## Integration

Seamlessly integrates with:
- Preprocessing pipeline (data extraction)
- Indexing system (Weaviate vector store)
- Retrieval module (semantic search + re-ranking)

## Environment Variables

```bash
OPENAI_API_KEY=<your_openai_key>         # Required
LLM_MODEL=gpt-4-turbo-preview            # Optional
LLM_TEMPERATURE=0.1                       # Optional
LLM_MAX_TOKENS=1500                       # Optional
WEAVIATE_URL=<your_weaviate_url>         # Required
WEAVIATE_API_KEY=<your_weaviate_key>     # Required
```

