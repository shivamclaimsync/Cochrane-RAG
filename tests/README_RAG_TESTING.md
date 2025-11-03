# RAG System Testing

This directory contains test questions and a test script to evaluate the RAG system's performance.

## Files

- `test_questions_rag_system.json` - Comprehensive set of 57 test questions organized by category
- `test_rag_system_questions.py` - Test script to run questions through the RAG system
- `load_test_questions.py` - Utility functions to load and access test questions

## Quick Start

### Test All Questions

```bash
python3 tests/test_rag_system_questions.py
```

### Test a Limited Number of Questions

```bash
python3 tests/test_rag_system_questions.py --limit 10
```

### Test a Specific Category

```bash
python3 tests/test_rag_system_questions.py --category treatment_effectiveness
```

### Test Without Reranker (Faster)

```bash
python3 tests/test_rag_system_questions.py --no-reranker
```

### Save Results to Custom File

```bash
python3 tests/test_rag_system_questions.py --output my_results.json
```

### Verbose Output

```bash
python3 tests/test_rag_system_questions.py --verbose
```

## Available Categories

- `treatment_effectiveness` - Questions about treatment effectiveness
- `comparative_questions` - Questions comparing different treatments
- `safety_and_adverse_effects` - Questions about safety and adverse effects
- `statistical_and_outcomes` - Questions about statistical outcomes
- `specific_conditions` - Questions about specific medical conditions
- `population_specific` - Questions about specific populations
- `complex_multipart_queries` - Complex questions with multiple parts
- `methodology_and_evidence_quality` - Questions about methodology and evidence quality
- `pico_based_queries` - Questions following PICO framework

## Test Results Format

Results are saved as JSON with the following structure:

```json
{
  "test_metadata": {
    "timestamp": "2025-11-03T14:58:50.885585",
    "total_questions": 57,
    "total_time": 684.23,
    "avg_time_per_question": 12.00
  },
  "results": [
    {
      "question": "...",
      "question_num": 1,
      "category": "treatment_effectiveness",
      "success": true,
      "answer": "...",
      "num_sources": 10,
      "sources": [...],
      "quality_summary": "...",
      "statistical_summary": "...",
      "retrieval_time": 12.53,
      "error": null
    }
  ],
  "summary": {
    "total_tested": 57,
    "successful": 55,
    "failed": 2,
    "success_rate": 96.5,
    "average_sources_per_question": 7.7,
    "average_retrieval_time": 12.00,
    "results_by_category": {...}
  }
}
```

## Performance Notes

- Average retrieval time per question: ~10-15 seconds
- Testing all 57 questions will take approximately 10-15 minutes
- Results include full answers, sources, and metadata for analysis
- Use `--limit` for quick testing during development

## Usage in Code

You can also use the test script programmatically:

```python
from tests.test_rag_system_questions import RAGSystemTester
from tests.load_test_questions import load_test_questions

# Initialize tester
tester = RAGSystemTester(use_reranker=True, verbose=False)

# Load questions
data = load_test_questions()

# Test all questions
results = tester.test_all(data, limit=10)

# Print summary
tester.print_summary(results)

# Save results
tester.save_results(results, "my_results.json")

# Close connections
tester.close()
```

