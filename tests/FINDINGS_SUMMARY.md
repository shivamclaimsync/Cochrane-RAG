# Root Cause Findings Summary

## Confirmed Root Cause

**The primary issue is limited document indexing combined with specific document unavailability.**

### Key Findings:

1. **Thrombopoietin Documents NOT Indexed**
   - 0 documents indexed for "thrombopoietin" keyword
   - 2 files exist in output directory (`thrombopoietin_receptor_agonis_*.json`)
   - **This directly explains why questions about TPO-RAs get "no direct evidence"**

2. **Limited Coverage for Related Topics**
   - Only 10 documents indexed for each keyword search:
     - platelet_transfusion: 10 indexed
     - sickle_cell: 10 indexed  
     - red_blood_cell_transfusion: 10 indexed
   - But many more files exist:
     - platelet: 72 files exist
     - sickle_cell: 34 files exist
     - transfusion: 71 files exist

3. **Indexing Limit Restriction**
   - Only 546 documents indexed total
   - 17,054 files available in output directory
   - **Only 3.2% of available documents are indexed**

4. **Blood Disorders Underrepresented**
   - Only 4 documents indexed in "Blood disorders" topic category
   - Many test questions focus on blood disorders topics

## Why This Causes "No Direct Evidence" Answers

1. Query: "What is the effectiveness of thrombopoietin receptor agonists..."
2. Retrieval: Finds 10 related documents (venous thrombo-embolic events, platelet therapy, etc.)
3. Problem: The exact document about TPO-RAs is NOT indexed (0 results for "thrombopoietin")
4. LLM receives: Related but not directly relevant documents
5. LLM correctly responds: "No direct evidence available" because the retrieved docs don't answer the specific question

## The Retrieval System IS Working

- It successfully finds 9-10 sources per question
- The sources are semantically related to the query
- The problem is that the **exact** documents needed aren't in the index

## Solutions

### Immediate Fix:
```bash
# Re-index with higher limit or no limit
python3 run_indexing.py  # But first update limit in run_indexing.py
```

### Update run_indexing.py:
```python
# Change line with limit=500 to:
pipeline.index_processed_documents(
    processed_dir=output_dir,
    skip_processed=False,
    limit=None  # or limit=5000+ to include more documents
)
```

### Priority Indexing:
Index all "Blood disorders" topic files first, as they're heavily represented in test questions.

## Verification Checklist

- [x] Confirmed: Only 546/17,054 documents indexed
- [x] Confirmed: 0 thrombopoietin documents indexed (but 2 files exist)
- [x] Confirmed: Only 4 "Blood disorders" documents indexed
- [x] Confirmed: Retrieval system working (finding related docs)
- [x] Confirmed: LLM working correctly (identifying irrelevance)

## Next Steps

1. **Increase indexing limit** in `run_indexing.py`
2. **Re-run indexing** to include more documents
3. **Prioritize indexing** of blood disorders and related topics
4. **Re-run tests** to verify improvement

