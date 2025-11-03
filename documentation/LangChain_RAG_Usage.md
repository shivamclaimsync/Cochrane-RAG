# LangChain Medical RAG System - Usage Guide

## Overview

The Cochrane Medical RAG (Retrieval-Augmented Generation) system provides evidence-based medical question answering using Cochrane systematic reviews. It combines state-of-the-art retrieval, custom medical re-ranking, and LLM generation to deliver accurate, well-cited medical information.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### 1. Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```bash
# Vector Database (Weaviate)
WEAVIATE_URL=your_weaviate_cluster_url
WEAVIATE_API_KEY=your_weaviate_api_key

# Embeddings (HuggingFace)
HUGGINGFACE_API_KEY=your_huggingface_api_key

# LLM Provider (choose one or multiple)
OPENAI_API_KEY=your_openai_api_key          # For GPT-4, GPT-3.5
ANTHROPIC_API_KEY=your_anthropic_api_key    # For Claude

# Optional: LLM Configuration
LLM_PROVIDER=openai                          # Options: openai, anthropic, ollama
LLM_MODEL=gpt-4-turbo-preview               # Or your preferred model
LLM_TEMPERATURE=0.1                          # Lower for factual medical responses
LLM_MAX_TOKENS=1500                          # For detailed explanations
```

### 3. Verify Installation

```bash
# Check system status
python -c "from src.generation.medical_rag_system import print_system_info; print_system_info()"
```

---

## Quick Start

### Python API - Simple Usage

```python
from src.generation.medical_rag_system import CochraneMedicalRAG

# Initialize the system
rag = CochraneMedicalRAG()

# Ask a medical question
question = "What is the effectiveness of vitamin C for preventing colds?"
result = rag.ask(question)

print(result)

# Close when done
rag.close()
```

### Command-Line Interface

```bash
# Interactive mode
python src/generation/cli.py

# Single question
python src/generation/cli.py --question "Is zinc effective for treating colds?"

# With specific provider
python src/generation/cli.py --provider anthropic --model claude-3-sonnet

# Conversational mode
python src/generation/cli.py --conversational
```

---

## System Architecture

### 3-Layer Retrieval Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   MEDICAL QUERY INPUT                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Initial Retrieval (Top-50)                        │
│  - Semantic search with medical embeddings                   │
│  - Metadata filtering (topic, quality, section)             │
│  - PubMedBERT indexed, Sentence Transformers for queries    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: Medical Re-ranking (Top-10)                       │
│  - Quality Score Weight (30%): Grade A > B > C              │
│  - Statistical Relevance (20%)                              │
│  - Section Relevance (20%)                                  │
│  - Base Semantic Score (30%)                                │
│  - Optional: Cross-encoder refinement                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: LLM Generation                                     │
│  - Medical prompts with evidence-based guidelines            │
│  - Context formatting with citations                         │
│  - Response formatting with quality indicators               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            FORMATTED MEDICAL RESPONSE                        │
│  - Answer with evidence                                      │
│  - Quality summary                                           │
│  - Statistical support                                       │
│  - Citations and sources                                     │
│  - Limitations                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage Examples

### Example 1: Basic Medical Question

```python
from src.generation.medical_rag_system import CochraneMedicalRAG

rag = CochraneMedicalRAG(verbose=False)

question = "What is the effectiveness of vitamin D for COVID-19?"
result = rag.ask(question, format="string")

print(result)
rag.close()
```

### Example 2: Statistical Evidence Query

```python
rag = CochraneMedicalRAG(verbose=False)

question = "What is the statistical evidence for aspirin in cardiovascular disease prevention?"
result = rag.ask(question, format="dict")

print(f"Answer: {result['answer']}\n")
print(f"Statistical Summary: {result['statistical_summary']}")
print(f"Quality Summary: {result['quality_summary']}")

rag.close()
```

### Example 3: Search-Only Mode (No LLM)

```python
rag = CochraneMedicalRAG(verbose=False)

# Search without LLM generation
results = rag.search(
    query="corticosteroids asthma",
    filters={'quality_grade': 'A'},  # Only Grade A reviews
    top_k=5
)

for idx, result in enumerate(results, 1):
    print(f"[{idx}] {result['metadata']['title']}")
    print(f"    Quality: Grade {result['metadata']['quality_grade']}")
    print(f"    Topic: {result['metadata']['topic_name']}")

rag.close()
```

### Example 4: Batch Processing

```python
rag = CochraneMedicalRAG(verbose=False)

questions = [
    "Is zinc effective for treating the common cold?",
    "What is the evidence for probiotics in preventing antibiotic-associated diarrhea?"
]

results = rag.batch_ask(questions, format="dict")

for result in results:
    print(f"\nQ: {result['question']}")
    print(f"A: {result['answer'][:200]}...")
    print(f"Sources: {result['metadata']['num_sources']}")

rag.close()
```

### Example 5: Conversational Mode

```python
rag = CochraneMedicalRAG(conversational=True, verbose=False)

# First question
r1 = rag.ask("What is the effectiveness of CBT for depression?")
print(f"Answer 1: {r1}\n")

# Follow-up question (uses conversation context)
r2 = rag.ask("How does it compare to medication?")
print(f"Answer 2: {r2}\n")

# Another follow-up
r3 = rag.ask("What about long-term effects?")
print(f"Answer 3: {r3}\n")

# View chat history
history = rag.chain.get_history()
print(f"Total exchanges: {len(history)}")

rag.close()
```

### Example 6: Different Output Formats

```python
rag = CochraneMedicalRAG(verbose=False)

question = "Is melatonin effective for insomnia?"

# String format (formatted, human-readable)
string_result = rag.ask(question, format="string")

# Markdown format
md_result = rag.ask(question, format="markdown")

# JSON format (serializable)
json_result = rag.ask(question, format="json")

# Dict format (most detailed, includes source documents)
dict_result = rag.ask(question, format="dict")

rag.close()
```

### Example 7: Custom LLM Configuration

```python
# Use Claude instead of GPT-4
rag = CochraneMedicalRAG(
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    verbose=True
)

# Use Ollama (local model)
rag_local = CochraneMedicalRAG(
    provider="ollama",
    model="llama2:70b",
    verbose=True
)

# Disable re-ranker for faster results
rag_fast = CochraneMedicalRAG(
    use_reranker=False,
    top_k=5
)
```

---

## API Reference

### `CochraneMedicalRAG`

Main class for the medical RAG system.

#### Constructor

```python
CochraneMedicalRAG(
    provider: str = "openai",
    model: Optional[str] = None,
    use_reranker: bool = True,
    top_k: int = 10,
    conversational: bool = False,
    verbose: bool = True,
    **kwargs
)
```

**Parameters:**
- `provider`: LLM provider ("openai", "anthropic", "ollama")
- `model`: Model name (None = use default)
- `use_reranker`: Enable medical re-ranker (recommended)
- `top_k`: Number of documents to retrieve
- `conversational`: Enable conversational mode with chat history
- `verbose`: Print initialization info

#### Methods

##### `ask(question, format="string", **kwargs)`

Ask a medical question and get evidence-based answer.

**Parameters:**
- `question` (str): Medical question
- `format` (str): Output format ("string", "markdown", "json", "dict")

**Returns:** Formatted response (type depends on format parameter)

**Example:**
```python
result = rag.ask("What is the effectiveness of vitamin C?", format="string")
```

##### `batch_ask(questions, format="string", **kwargs)`

Ask multiple questions in batch.

**Parameters:**
- `questions` (List[str]): List of medical questions
- `format` (str): Output format

**Returns:** List of formatted responses

##### `search(query, filters=None, top_k=None)`

Search for relevant Cochrane review chunks without LLM generation.

**Parameters:**
- `query` (str): Search query
- `filters` (Dict): Filters (level, topic, quality_grade, section, statistical_only)
- `top_k` (int): Number of results

**Returns:** List of relevant documents with metadata

**Example:**
```python
results = rag.search(
    query="diabetes treatment",
    filters={'quality_grade': 'A', 'topic': 'Metabolic'},
    top_k=5
)
```

##### `get_stats()`

Get system statistics.

**Returns:** Dictionary with system statistics

##### `clear_history()`

Clear chat history (conversational mode only).

##### `close()`

Close system and cleanup resources.

---

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `WEAVIATE_URL` | Yes | Weaviate cluster URL | - |
| `WEAVIATE_API_KEY` | Yes | Weaviate API key | - |
| `HUGGINGFACE_API_KEY` | Yes | HuggingFace API key | - |
| `OPENAI_API_KEY` | No* | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | No* | Anthropic API key | - |
| `LLM_PROVIDER` | No | LLM provider | "openai" |
| `LLM_MODEL` | No | Model name | Provider default |
| `LLM_TEMPERATURE` | No | Sampling temperature | 0.1 |
| `LLM_MAX_TOKENS` | No | Max tokens to generate | 1500 |

*At least one LLM provider API key is required

### Recommended Models

**Best Quality:**
- OpenAI: `gpt-4-turbo-preview`
- Anthropic: `claude-3-opus-20240229`
- Ollama: `meditron:70b` (medical-specific)

**Balanced (Recommended):**
- OpenAI: `gpt-4-turbo-preview`
- Anthropic: `claude-3-sonnet-20240229`
- Ollama: `llama2:70b`

**Fast/Cost-Effective:**
- OpenAI: `gpt-3.5-turbo`
- Anthropic: `claude-3-haiku-20240307`
- Ollama: `llama2:13b`

---

## Advanced Features

### Custom Medical Re-ranking

The system uses a multi-factor re-ranking algorithm:

```python
from src.retrieving.reranker import MedicalReranker

# Custom weights
reranker = MedicalReranker(
    weight_quality=0.40,      # Prioritize quality more
    weight_statistical=0.30,  # Prioritize statistical evidence
    weight_section=0.15,
    weight_semantic=0.15
)

# Use in retrieval pipeline
documents = retriever.get_relevant_documents(query)
scored_docs = reranker.rerank(documents, query, top_k=10)
```

### Cross-Encoder Re-ranking (Optional)

For even better precision using HuggingFace Inference API:

```python
from src.retrieving.cross_encoder_reranker import CrossEncoderReranker

# Initialize cross-encoder (requires HUGGINGFACE_API_KEY)
cross_encoder = CrossEncoderReranker(
    model_name="cross-encoder/ms-marco-MiniLM-L-12-v2"
)

# Re-rank with cross-encoder
scored_docs = cross_encoder.rerank(query, documents, top_k=10)
```

**Note:** Requires `HUGGINGFACE_API_KEY` environment variable. Falls back to distance-based scoring if not available.

### Hybrid Re-ranking

Combine both approaches:

```python
from src.retrieving.cross_encoder_reranker import HybridReranker

hybrid = HybridReranker(
    stage1_top_k=20,  # Medical reranker
    stage2_top_k=10   # Cross-encoder refinement
)

final_docs = hybrid.rerank(query, documents)
```

### Custom Prompts

Create specialized prompts for different query types:

```python
from src.generation.prompts import (
    create_statistical_qa_prompt,
    create_safety_qa_prompt,
    create_effectiveness_qa_prompt
)

# Use statistical prompt
stat_prompt = create_statistical_qa_prompt()

# Use in chain
from src.generation.rag_chain import MedicalRAGChain

chain = MedicalRAGChain(llm=llm, retriever=retriever)
# Chain will automatically select appropriate prompt based on query
```

---

## Troubleshooting

### Issue: "OPENAI_API_KEY not set in environment"

**Solution:** Add your API key to `.env` file:
```bash
OPENAI_API_KEY=sk-...your_key_here...
```

### Issue: "Failed to connect to Weaviate"

**Solutions:**
1. Verify `WEAVIATE_URL` and `WEAVIATE_API_KEY` in `.env`
2. Check Weaviate cluster is running
3. Verify network connectivity

### Issue: "No results returned"

**Solutions:**
1. Check if data is indexed: Run `demo_retrieval_complete.py`
2. Try broader query terms
3. Remove or relax filters
4. Increase `top_k` parameter

### Issue: "HF API error: 503"

**Solutions:**
1. HuggingFace model may be loading (wait 30s and retry)
2. Check `HUGGINGFACE_API_KEY` is valid
3. Try different embedding model

### Issue: "Query embedding dimension mismatch"

**Solution:** The system handles dimension differences automatically. If issues persist:
- Indexed data uses PubMedBERT (768-dim)
- Queries use Sentence Transformers (384 or 768-dim)
- Re-ranker bridges any semantic gap

### Issue: Slow responses

**Solutions:**
1. Disable re-ranker: `use_reranker=False`
2. Reduce `top_k` value
3. Use faster model (GPT-3.5, Claude Haiku)
4. Disable cross-encoder if enabled

---

## Best Practices

### For Medical Accuracy
1. **Always enable re-ranker** for medical queries
2. **Use Grade A filter** for clinical decision support
3. **Review source quality** in results
4. **Consider limitations** mentioned in responses

### For Performance
1. **Cache common queries** at application level
2. **Use batch processing** for multiple questions
3. **Adjust `top_k`** based on use case (5-10 usually sufficient)
4. **Disable features** you don't need (re-ranker, cross-encoder)

### For Production
1. **Set up monitoring** for API usage and costs
2. **Implement rate limiting** for user queries
3. **Add error handling** and fallback mechanisms
4. **Log queries** for quality improvement
5. **Validate responses** against known-good examples

---

## Examples & Demos

### Run Comprehensive Demo

```bash
# Run all demos
python demo_rag_system.py

# Run specific demo
python demo_rag_system.py 1  # Simple question
python demo_rag_system.py 5  # Search-only mode
```

### Interactive CLI

```bash
# Start interactive session
python src/generation/cli.py

# Available commands in CLI:
#   /help     - Show help
#   /search   - Search mode
#   /stats    - System statistics
#   /history  - Chat history
#   /export   - Export response
#   /quit     - Exit
```

---

## Support & Resources

- **Documentation**: `documentation/` directory
- **Examples**: `demo_rag_system.py`
- **System Design**: `documentation/Expert_RAG_System_Approach.md`
- **Architecture**: `documentation/RAG_System_Flowchart.md`

---

## Version Information

- **System Version**: 1.0.0
- **LangChain Version**: >=0.1.0
- **Last Updated**: January 2025

---

**Note**: This system is designed for medical research and education. Always consult qualified healthcare professionals for clinical decisions.

