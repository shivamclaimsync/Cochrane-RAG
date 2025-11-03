# Cochrane Review Section and Subsection Format

## Overview

This document defines the standardized hierarchical structure for extracting sections and subsections from Cochrane systematic reviews. The format ensures consistent, structured extraction of all major components of Cochrane reviews.

## Major Sections (Container Sections)

### 1. Abstract
**Purpose**: Summary of the entire review including background, objectives, methods, results, and conclusions.

**Subsections**:
- `available_in` - Language availability information
- `background` - Brief description of the condition/intervention
- `objectives` - Primary and secondary objectives
- `search_methods` - Database searches and search strategies
- `selection_criteria` - Inclusion/exclusion criteria for studies
- `data_collection_and_analysis` - Methods for data extraction and analysis
- `main_results` - Key findings and statistical results
- `authors_conclusions` - Main conclusions and implications

### 2. PICOs
**Purpose**: Structured framework defining the review question components.

**Subsections**:
- `population` - Target population characteristics
- `intervention` - Interventions being evaluated
- `comparison` - Control or comparison interventions
- `outcome` - Primary and secondary outcomes

### 3. Plain Language Summary
**Purpose**: Non-technical summary for patients and the public.

**Subsections**:
- `available_in` - Language availability information
- `background` - Simple explanation of the condition
- `clinical_question` - What the review aimed to find out
- `study_characteristics` - Description of included studies
- `main_results` - Key findings in plain language
- `quality_of_evidence` - Assessment of evidence quality

### 4. Authors' Conclusions
**Purpose**: Detailed conclusions with practice and research implications.

**Subsections**:
- `available_in` - Language availability information
- `implications_for_practice` - Clinical practice recommendations
- `implications_for_research` - Future research directions

### 5. Summary of Findings
**Purpose**: Structured tables presenting key outcomes with quality assessments.

**Subsections**:
- Usually contains structured table data (no standard subsections)

### 6. Background
**Purpose**: Detailed context and rationale for the review.

**Subsections**:
- `available_in` - Language availability information
- `description_of_the_condition` - Detailed condition description
- `description_of_the_intervention` - Intervention details
- `how_the_intervention_might_work` - Theoretical mechanisms
- `why_it_is_important_to_do_this_review` - Rationale and gaps

### 7. Methods
**Purpose**: Detailed methodology for conducting the review.

**Subsections**:
- `available_in` - Language availability information
- `criteria_for_considering_studies_for_this_review` - Study selection criteria
- `search_methods_for_identification_of_studies` - Search strategies
- `data_collection_and_analysis` - Data extraction methods
- `selection_of_studies` - Study selection process
- `data_extraction_and_management` - Data collection procedures
- `assessment_of_risk_of_bias_in_included_studies` - Quality assessment
- `measures_of_treatment_effect` - Statistical methods
- `unit_of_analysis_issues` - Analysis considerations
- `dealing_with_missing_data` - Missing data handling
- `assessment_of_heterogeneity` - Heterogeneity evaluation
- `assessment_of_reporting_biases` - Publication bias assessment
- `data_synthesis` - Meta-analysis methods
- `subgroup_analysis_and_investigation_of_heterogeneity` - Subgroup analyses
- `sensitivity_analysis` - Sensitivity testing
- `trial_sequential_analysis` - Sequential analysis methods
- `summary_of_findings_tables` - GRADE assessments

### 8. Results
**Purpose**: Detailed presentation of review findings.

**Subsections**:
- `description_of_studies` - Characteristics of included studies
- `results_of_the_search` - Search results summary
- `included_studies` - Details of selected studies
- `excluded_studies` - Reasons for exclusion
- `risk_of_bias_in_included_studies` - Quality assessment results
- `methodology_characteristics` - Study design details
- `patient_characteristics` - Participant demographics
- `interventions` - Intervention details
- `outcomes` - Outcome measurements
- `leukoreduction_definition` - Specific intervention definitions
- `type_of_filters` - Technical specifications
- `control_groups` - Control group details
- `cointervention` - Additional interventions

### 9. Discussion
**Purpose**: Interpretation and contextualization of results.

**Subsections**:
- `available_in` - Language availability information
- `summary_of_main_results` - Key findings summary
- `overall_completeness_and_applicability_of_evidence` - Evidence assessment
- `quality_of_the_evidence` - GRADE quality ratings
- `potential_biases_in_the_review_process` - Review limitations
- `agreements_and_disagreements_with_other_studies_or_reviews` - Comparison with other evidence
- `overall_completeness_of_evidence` - Evidence completeness
- `applicability_of_evidence` - Clinical applicability

## Standalone Sections

### 10. Objectives
**Purpose**: Detailed statement of review objectives.
**Note**: No subsections - contains complete objective statements.

## JSON Structure Format

```json
{
  "metadata": {
    "source_file": "filename.json",
    "title": "Review Title",
    "doi": "10.1002/14651858.CD000000.pub1",
    "authors": ["Author1", "Author2"],
    "url": "https://www.cochranelibrary.com/...",
    "timestamp": 1234567890,
    "extraction_date": "2025-01-01T00:00:00",
    "sections_extracted": ["abstract", "picos", "plain_language_summary"],
    "section_count": 10,
    "subsection_count": 35,
    "total_extracted": 45,
    "content_length": 50000
  },
  "sections": {
    "abstract": {
      "content": "Full abstract content...",
      "subsections": {
        "available_in": "English Español Français",
        "background": "Background content...",
        "objectives": "Objectives content...",
        "search_methods": "Search methods content...",
        "selection_criteria": "Selection criteria content...",
        "data_collection_and_analysis": "Data collection content...",
        "main_results": "Main results content...",
        "authors_conclusions": "Authors conclusions content..."
      }
    },
    "picos": {
      "content": "Full PICOs content...",
      "subsections": {
        "population": "Population details...",
        "intervention": "Intervention details...",
        "comparison": "Comparison details...",
        "outcome": "Outcome details..."
      }
    },
    "objectives": "Complete objectives content without subsections"
  },
  "quality": {
    "score": 95,
    "grade": "A",
    "content_length": 50000,
    "drug_count": 5,
    "condition_count": 2,
    "extraction_method": "hierarchical"
  }
}
```

## Quality Scoring System

### Grade A (100/100)
- 8+ major sections extracted
- Complete hierarchical structure
- All expected subsections present
- High content quality

### Grade B (78-99/100)
- 6-7 major sections extracted
- Good hierarchical structure
- Most subsections present
- Good content quality

### Grade C (42-77/100)
- 4-5 major sections extracted
- Basic hierarchical structure
- Some subsections present
- Adequate content quality

## Special Cases

### Reviews with No Included Studies
Some reviews may have fewer sections if they found no eligible studies:
- Abstract (with "no studies found" results)
- PICOs
- Plain Language Summary
- Authors' Conclusions
- Background
- Objectives

### Protocol Reviews
Protocol reviews may have different section structures focused on planned methodology.

### Withdrawn Reviews
Some reviews may be withdrawn and have minimal content.

## Extraction Patterns

### Section Boundary Detection
- Major sections identified by exact header matches
- Subsections identified within major section boundaries
- Content cleaned to remove navigation and TOC elements
- Hierarchical relationships preserved

### Content Quality Indicators
- Language availability information
- Structured content with clear subsections
- Statistical results and confidence intervals
- GRADE quality assessments
- Clinical implications and recommendations

## Usage Guidelines

1. **Consistency**: Always use the exact section and subsection names as defined
2. **Hierarchy**: Maintain the parent-child relationship between sections and subsections
3. **Completeness**: Extract all available content within each section
4. **Quality**: Ensure content is clean and properly formatted
5. **Validation**: Verify that extracted content matches the original structure

This format ensures standardized, high-quality extraction of Cochrane systematic reviews for analysis, research, and clinical decision-making applications.
