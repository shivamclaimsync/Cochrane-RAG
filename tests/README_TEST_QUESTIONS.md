# Test Questions for RAG System Evaluation

This directory contains test questions specifically designed to evaluate the RAG system based on the indexed Cochrane reviews in Weaviate.

## Files

- **`test_questions_rag_system.json`**: JSON file containing 57 test questions organized into 9 categories
- **`load_test_questions.py`**: Python utility script to load and work with test questions

## Question Categories

1. **Treatment Effectiveness** (10 questions)
   - Questions about the effectiveness of specific treatments and interventions

2. **Comparative Questions** (7 questions)
   - Questions comparing different treatments or strategies

3. **Safety and Adverse Effects** (7 questions)
   - Questions about safety profiles and adverse events

4. **Statistical and Outcomes** (8 questions)
   - Questions about specific outcomes, mortality, bleeding rates, etc.

5. **Specific Conditions** (7 questions)
   - Questions about treatments for specific medical conditions

6. **Population Specific** (4 questions)
   - Questions targeting specific patient populations (adults, children, elderly)

7. **Complex Multipart Queries** (5 questions)
   - Multi-faceted questions requiring comprehensive answers

8. **Methodology and Evidence Quality** (5 questions)
   - Questions about study methodology and evidence quality (GRADE, risk of bias)

9. **PICO-Based Queries** (4 questions)
   - Questions structured around Population, Intervention, Comparison, Outcome framework

## Usage

### Basic Usage

```python
from tests.load_test_questions import load_test_questions, get_all_questions, get_questions_by_category

# Load all questions
data = load_test_questions()

# Get all questions as a flat list
all_questions = get_all_questions(data)
print(f"Total: {len(all_questions)} questions")

# Get questions from a specific category
treatment_qs = get_questions_by_category("treatment_effectiveness", data)
```

### Using with RAG System

```python
from tests.load_test_questions import get_all_questions
from src.retrieving.retriever import CochraneRetriever

# Initialize retriever
retriever = CochraneRetriever()

# Get test questions
questions = get_all_questions()

# Test a question
query = questions[0]
results = retriever.search(query, limit=5)
print(retriever.format_results(results))
```

### Running the Example

```bash
python3 tests/load_test_questions.py
```

This will display:
- Total number of questions
- Questions organized by category
- Sample questions from each category

## Question Selection Criteria

All questions in this collection:
- ✅ Reference topics and conditions that exist in the indexed data
- ✅ Use medical terminology found in Cochrane reviews
- ✅ Cover multiple query types (factual, comparative, statistical)
- ✅ Test different aspects of the RAG system
- ✅ Include questions of varying complexity levels
- ✅ Are based on actual indexed documents

## Topics Covered

Questions are based on indexed data covering:
- Blood disorders (thrombocytopenia, platelet transfusions, red blood cell transfusions)
- Sickle cell disease
- Bone marrow failure disorders
- Haematological malignancies
- Allergic conditions
- Child health
- And more...

## Testing Recommendations

1. **Start with Simple Questions**: Begin with single-aspect questions (e.g., treatment effectiveness)
2. **Progress to Complex Queries**: Test multipart questions that require comprehensive answers
3. **Test Different Categories**: Evaluate how well the system handles different question types
4. **Check Retrieval Quality**: Verify that retrieved chunks are relevant to the query
5. **Evaluate Response Accuracy**: Assess whether the generated answers are factually correct and complete

## Example Evaluation Workflow

```python
from tests.load_test_questions import get_all_questions
from src.retrieving.retriever import CochraneRetriever

retriever = CochraneRetriever()
questions = get_all_questions()

# Evaluate retrieval quality
for question in questions[:5]:  # Test first 5 questions
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"{'='*80}")
    
    results = retriever.search(question, limit=5)
    
    # Check relevance
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Relevance Score: {1 - result.distance:.4f}")
        print(f"  Topic: {result.topic_name}")
        print(f"  Section: {result.section_name}")
        print(f"  Preview: {result.content[:200]}...")

retriever.close()
```

## Notes

- Questions are designed to test the system's ability to retrieve relevant information from indexed Cochrane reviews
- All questions should have answers in the indexed data (if indexing was successful)
- Some questions may require retrieval from multiple documents
- Complex queries may need query decomposition to retrieve all relevant information

