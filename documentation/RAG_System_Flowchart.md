# Cochrane RAG System Flowchart

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COCHRANE RAG SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAW DATA      │    │   PREPROCESSING │    │   VECTOR STORE  │    │   RETRIEVAL     │
│   (17,324       │───▶│   PIPELINE      │───▶│   (Weaviate)    │───▶│   SYSTEM        │
│   Reviews)      │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HIERARCHICAL  │    │   CHUNKING      │    │   EMBEDDINGS    │    │   RESPONSE      │
│   SECTIONS      │    │   STRATEGY      │    │   (Medical)     │    │   GENERATION    │
│   (17,054       │    │                 │    │                 │    │                 │
│   Files)        │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Detailed System Flow

### 1. DATA INGESTION & PREPROCESSING FLOW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA INGESTION PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────────────┘

Raw Cochrane JSON Files (17,324)
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA VALIDATION                                    │
│  • Check for required fields (title, abstract, full_content)                    │
│  • Validate JSON structure                                                      │
│  • Quality score assessment (A, B, C grades)                                   │
│  • Topic classification verification                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            HIERARCHICAL EXTRACTION                              │
│  • Abstract with subsections (Background, Objectives, Results, Conclusions)     │
│  • PICOs (Population, Intervention, Comparison, Outcome)                       │
│  • Methods (Search strategy, Selection criteria, Data analysis)                │
│  • Results (Study characteristics, Outcomes, Statistical data)                 │
│  • Discussion (Main results, Quality of evidence, Limitations)                 │
│  • Authors' conclusions (Implications for practice/research)                   │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONTENT ENRICHMENT                                 │
│  • PICO element extraction and structuring                                      │
│  • Statistical data parsing (CI, p-values, effect sizes)                       │
│  • Medical entity recognition (drugs, conditions, procedures)                   │
│  • Study quality indicators (GRADE, risk of bias)                              │
│  • Evidence hierarchy classification                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2. CHUNKING & EMBEDDING STRATEGY

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            CHUNKING STRATEGY                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

Hierarchical Content
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          MULTI-LEVEL CHUNKING ✅ IMPLEMENTED                   │
│                                                                                 │
│  Level 1: Document Level (Full Review)                                         │
│  ├── Metadata (title, authors, DOI, topic, quality)                            │
│  ├── Abstract summary                                                           │
│  └── Key findings overview                                                      │
│                                                                                 │
│  Level 2: Section Level (Major Sections)                                       │
│  ├── Abstract (with subsections)                                               │
│  ├── PICOs (structured PICO elements)                                          │
│  ├── Methods (search, selection, analysis)                                     │
│  ├── Results (study characteristics, outcomes)                                 │
│  ├── Discussion (main results, quality, limitations)                           │
│  └── Authors' conclusions (implications)                                       │
│                                                                                 │
│  Level 3: Subsection Level (Detailed Components)                               │
│  ├── Background, Objectives, Search methods                                    │
│  ├── Main results, Statistical findings                                        │
│  ├── Quality of evidence, Risk of bias                                         │
│  └── Implications for practice/research                                        │
│                                                                                 │
│  Level 4: Paragraph Level (Fine-grained)                                       │
│  ├── Individual paragraphs for precise retrieval                               │
│  ├── Statistical statements                                                    │
│  └── Clinical recommendations                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            EMBEDDING GENERATION                                 │
│                                                                                 │
│  Dense Embeddings (70% weight):                                                │
│  ├── microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract                      │
│  ├── dmis-lab/biobert-base-cased-v1.1                                          │
│  ├── allenai/specter (scientific papers)                                       │
│  └── Custom fine-tuned on Cochrane data                                        │
│                                                                                 │
│  Sparse Embeddings (30% weight):                                               │
│  ├── BM25 for exact medical term matching                                      │
│  ├── SPLADE for learned sparse retrieval                                       │
│  └── Custom medical vocabulary (drugs, conditions, procedures)                 │
│                                                                                 │
│  Metadata Embeddings:                                                          │
│  ├── Topic classification vectors                                              │
│  ├── Quality score embeddings                                                  │
│  ├── PICO element vectors                                                      │
│  └── Statistical significance indicators                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3. VECTOR STORE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            WEAVIATE VECTOR STORE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SCHEMA DESIGN                                      │
│                                                                                 │
│  Class: CochraneReview                                                          │
│  ├── Properties:                                                                │
│  │   ├── title (text)                                                          │
│  │   ├── abstract (text)                                                       │
│  │   ├── topic (text)                                                          │
│  │   ├── quality_grade (text: A/B/C)                                           │
│  │   ├── doi (text)                                                            │
│  │   ├── authors (text[])                                                      │
│  │   ├── pico_population (text)                                                │
│  │   ├── pico_intervention (text)                                              │
│  │   ├── pico_comparison (text)                                                │
│  │   ├── pico_outcome (text)                                                   │
│  │   ├── statistical_significance (boolean)                                    │
│  │   ├── effect_size (number)                                                  │
│  │   ├── confidence_interval (text)                                            │
│  │   ├── study_design (text)                                                   │
│  │   ├── evidence_level (text)                                                 │
│  │   └── publication_date (date)                                               │
│  │                                                                             │
│  ├── Vector Properties:                                                        │
│  │   ├── dense_embedding (vector[768])                                         │
│  │   ├── sparse_embedding (vector[sparse])                                     │
│  │   └── metadata_embedding (vector[256])                                      │
│  │                                                                             │
│  └── Indexing:                                                                 │
│      ├── HNSW for dense vectors                                                │
│      ├── Inverted index for sparse vectors                                     │
│      └── Filtering on metadata properties                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4. QUERY PROCESSING & RETRIEVAL FLOW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            QUERY PROCESSING PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────────────┘

Medical Query Input
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              QUERY ANALYSIS                                     │
│                                                                                 │
│  1. Intent Classification:                                                      │
│     ├── Treatment effectiveness                                                │
│     ├── Safety/adverse effects                                                 │
│     ├── Diagnostic accuracy                                                    │
│     ├── Prognostic factors                                                     │
│     └── Cost-effectiveness                                                     │
│                                                                                 │
│  2. PICO Extraction:                                                           │
│     ├── Population identification                                              │
│     ├── Intervention parsing                                                   │
│     ├── Comparison analysis                                                    │
│     └── Outcome specification                                                  │
│                                                                                 │
│  3. Medical Entity Recognition:                                                │
│     ├── Drug names and dosages                                                 │
│     ├── Medical conditions                                                     │
│     ├── Procedures and tests                                                   │
│     └── Patient demographics                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            MULTI-STAGE RETRIEVAL                                │
│                                                                                 │
│  Stage 0: Query Decomposition ✅ IMPLEMENTED                                   │
│  ├── Detect query complexity (and, compare, multiple intents)                  │
│  ├── LLM-based decomposition into 2-4 focused sub-queries                      │
│  ├── Extract intent per sub-query (effectiveness, safety, comparison, etc.)    │
│  ├── Keyword-based fallback for reliability                                    │
│  └── Plan retrieval strategy per intent                                        │
│                                                                                 │
│  Stage 1: Multi-Query Retrieval ✅ IMPLEMENTED                                 │
│  ├── Retrieve top 5 per sub-query (if decomposed)                              │
│  ├── Apply intent-specific filters (statistical_only, section_hint)            │
│  ├── Tag results with sub-query metadata                                       │
│  ├── Merge and deduplicate results (keep best score)                           │
│  └── Balance relevance with diversity across intents                           │
│                                                                                 │
│  Stage 2: Re-ranking (Top-K=10)                                                │
│  ├── Cross-encoder models for medical relevance                                │
│  ├── PICO element matching score                                               │
│  ├── Statistical significance weighting                                        │
│  ├── Study quality indicators                                                  │
│  └── Evidence hierarchy (systematic review > RCT > observational)             │
│                                                                                 │
│  Stage 3: Context Assembly ✅ IMPLEMENTED                                      │
│  ├── Include related sections (abstract + results + conclusions)               │
│  ├── Preserve hierarchical relationships                                       │
│  ├── Add metadata context (topic, quality, authors)                           │
│  ├── Statistical data formatting                                               │
│  └── Citation and DOI information                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      QUERY DECOMPOSITION EXAMPLE                               │
│                                                                                 │
│  User Query: "Are antifungal therapies safe and effective for allergic         │
│              fungal sinusitis in adults compared to placebo?"                   │
│                                                                                 │
│  Stage 0 Decomposition:                                                        │
│    ├── Detected: Multiple intents (safety + effectiveness + comparison)        │
│    ├── Generated 3 sub-queries:                                                │
│    │   1. [effectiveness] "Effectiveness of antifungal therapies for          │
│    │      allergic fungal sinusitis in adults"                                 │
│    │   2. [safety] "Safety and adverse effects of antifungal therapies for    │
│    │      allergic fungal sinusitis in adults"                                 │
│    │   3. [comparison] "Comparison of antifungal therapies vs placebo for     │
│    │      allergic fungal sinusitis in adults"                                 │
│    └── Each with section_hint="results"                                       │
│                                                                                 │
│  Stage 1 Multi-Query Retrieval:                                                │
│    ├── Retrieved 5 results per sub-query (15 total)                           │
│    ├── Applied statistical_only=False for all                                 │
│    ├── Tagged results with sub_query_intent                                   │
│    ├── Merged and deduplicated: 12 unique results                             │
│    └── Sorted by relevance with diversity: Top 10 final                       │
│                                                                                 │
│  Final Context: Comprehensive coverage of safety, effectiveness, and           │
│                 comparison aspects with relevant results from all sub-queries   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5. RESPONSE GENERATION & VALIDATION

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            RESPONSE GENERATION                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

Retrieved Context + Query
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              LLM PROCESSING                                     │
│                                                                                 │
│  Primary Models:                                                                │
│  ├── GPT-4/Claude-3 (medical reasoning)                                        │
│  ├── Local: Llama-2-70B medical variants                                       │
│  ├── Specialized: BioGPT, ClinicalBERT                                         │
│  └── Hybrid: Multiple models for different query types                          │
│                                                                                 │
│  Response Components:                                                           │
│  ├── Evidence-based summaries with statistical support                         │
│  ├── Clinical implications and recommendations                                 │
│  ├── Limitations and uncertainties                                             │
│  ├── Quality of evidence indicators                                            │
│  └── Citation and source information                                           │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              QUALITY VALIDATION                                 │
│                                                                                 │
│  1. Fact Checking:                                                              │
│     ├── Cross-reference with original studies                                  │
│     ├── Statistical claim validation                                           │
│     └── Citation accuracy verification                                         │
│                                                                                 │
│  2. Medical Accuracy:                                                           │
│     ├── Clinical appropriateness assessment                                    │
│     ├── Evidence hierarchy compliance                                          │
│     └── Bias detection and mitigation                                          │
│                                                                                 │
│  3. Expert Validation:                                                          │
│     ├── Medical professional review workflows                                  │
│     ├── Clinical decision support validation                                   │
│     └── Continuous improvement feedback                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FINAL RESPONSE                                     │
│                                                                                 │
│  • Evidence-based answer with statistical support                              │
│  • Clinical implications and recommendations                                   │
│  • Quality of evidence and limitations                                         │
│  • Source citations and DOI references                                         │
│  • Confidence indicators and uncertainty communication                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6. SYSTEM MONITORING & FEEDBACK LOOP

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            MONITORING & FEEDBACK                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PERFORMANCE METRICS                                │
│                                                                                 │
│  Technical Performance:                                                         │
│  ├── Retrieval Accuracy: >90% relevant results in top-10                       │
│  ├── Response Time: <2 seconds for complex queries                             │
│  ├── System Uptime: >99.5% availability                                        │
│  └── Scalability: 1000+ concurrent queries                                     │
│                                                                                 │
│  Medical Accuracy:                                                              │
│  ├── Factual Correctness: >95% accuracy                                        │
│  ├── Statistical Accuracy: >98% correct interpretations                        │
│  ├── Clinical Relevance: >90% appropriate responses                            │
│  └── Expert Validation: >85% medical professional approval                     │
│                                                                                 │
│  User Experience:                                                               │
│  ├── Query Understanding: >90% successful PICO extraction                      │
│  ├── Response Quality: >4.5/5 rating                                           │
│  ├── Clinical Utility: Demonstrated decision improvement                       │
│  └── Adoption Rate: >70% target user engagement                                │
└─────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONTINUOUS IMPROVEMENT                             │
│                                                                                 │
│  • Real-time performance monitoring                                            │
│  • User feedback collection and analysis                                       │
│  • Medical expert review and validation                                        │
│  • Model fine-tuning based on usage patterns                                   │
│  • Evidence base updates and new study integration                             │
│  • Bias detection and mitigation strategies                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            IMPLEMENTATION ROADMAP                               │
└─────────────────────────────────────────────────────────────────────────────────┘

Phase 1: Foundation (Weeks 1-2)
├── Set up Weaviate vector database with medical schema
├── Implement basic chunking and embedding pipeline
├── Create initial retrieval system with medical embeddings
└── Build basic query processing interface

Phase 2: Enhancement (Weeks 3-4)
├── Add PICO extraction and structured search
├── Implement medical entity recognition
├── Build re-ranking system with medical relevance
└── Add statistical parsing capabilities

Phase 3: Optimization (Weeks 5-6)
├── Fine-tune embedding models on Cochrane data
├── Implement hybrid search (dense + sparse)
├── Add evidence hierarchy awareness
└── Build medical query understanding system

Phase 4: Production (Weeks 7-8)
├── Deploy with medical-grade accuracy measures
├── Implement monitoring and feedback systems
├── Add expert validation workflows
└── Create medical professional interface
```

## Key Success Factors

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SUCCESS FACTORS                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

1. Medical Accuracy & Safety
   ├── Evidence-based responses with statistical support
   ├── Clinical appropriateness and safety considerations
   ├── Expert validation and continuous monitoring
   └── Regulatory compliance and ethical guidelines

2. Technical Performance
   ├── Fast and reliable query processing
   ├── Scalable architecture for growing data
   ├── Robust error handling and fallback mechanisms
   └── Comprehensive monitoring and alerting

3. User Experience
   ├── Intuitive medical query interface
   ├── Clear evidence presentation and interpretation
   ├── Actionable clinical recommendations
   └── Seamless integration with clinical workflows

4. Continuous Improvement
   ├── Real-time feedback collection and analysis
   ├── Regular model updates and fine-tuning
   ├── Evidence base expansion and maintenance
   └── Medical expert collaboration and validation
```

---

**Flowchart Version**: 1.0  
**Last Updated**: January 2025  
**Purpose**: Visual guide for Cochrane RAG System implementation
