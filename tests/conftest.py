"""
Pytest configuration and fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.core.data_models import (
    RawCochraneData, CleanedContent, ExtractedSections, SectionContent,
    PicoElements, MedicalEntities, QualityGrade, StudyDesign
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_raw_data():
    """Create sample raw Cochrane data for testing."""
    return RawCochraneData(
        url="https://example.com",
        number=1,
        timestamp=1234567890.0,
        title="Dehumidifiers for chronic asthma",
        doi="10.1002/14651858.CD000001.pub1",
        abstract="Humidity control measures in the home environment of patients with asthma have been recommended, since a warm humid environment favours the growth of house dust mites. However, there is no consensus about the usefulness of these measures.",
        authors=["Dr. Medical Author", "Dr. Another Author"],
        topic_name="Allergy & intolerance",
        topic_page=1,
        quality={"grade": "A", "score": 100},
        full_content="""Abstract
available in
English
Background
Humidity control measures in the home environment of patients with asthma have been recommended, since a warm humid environment favours the growth of house dust mites. However, there is no consensus about the usefulness of these measures.
Objectives
To study the effect of dehumidification of the home environment on asthma control.
Search methods
We searched the Cochrane Airways Group Specialised Register of trials, the Cochrane Central Register of Controlled Trials (CENTRAL), MEDLINE, EMBASE, and reference lists of articles. The most recent search was conducted in January 2013.
Selection criteria
We included randomised controlled trials (RCTs) comparing dehumidification with placebo or no treatment in patients with asthma.
Data collection and analysis
Two review authors independently assessed trial quality and extracted data. We contacted study authors for additional information.
Main results
A second trial has been added for the 2013 update of this review. The original open‐label trial compared an intervention consisting of mechanical ventilation heat recovery system with or without high efficiency vacuum cleaner fitted in 40 homes of patients with asthma who had positive tests for sensitivity to house dust mite. The trial showed a mean difference (MD) of 24.56 (95% CI 8.97 to 40.15) for evening peak flow. The morning peak flow showed no significant difference (MD 13.59; 95% CI -2.66 to 29.84). The p-value was < 0.05 for the primary outcome.
Authors' conclusions
There is limited evidence to support the use of dehumidification in the home environment for patients with asthma.

Background
Humidity control measures in the home environment of patients with asthma have been recommended, since a warm humid environment favours the growth of house dust mites. However, there is no consensus about the usefulness of these measures.

Objectives
To study the effect of dehumidification of the home environment on asthma control.

Search methods
We searched the Cochrane Airways Group Specialised Register of trials, the Cochrane Central Register of Controlled Trials (CENTRAL), MEDLINE, EMBASE, and reference lists of articles. The most recent search was conducted in January 2013.

Selection criteria
We included randomised controlled trials (RCTs) comparing dehumidification with placebo or no treatment in patients with asthma.

Data collection and analysis
Two review authors independently assessed trial quality and extracted data. We contacted study authors for additional information.

Main results
A second trial has been added for the 2013 update of this review. The original open‐label trial compared an intervention consisting of mechanical ventilation heat recovery system with or without high efficiency vacuum cleaner fitted in 40 homes of patients with asthma who had positive tests for sensitivity to house dust mite. The trial showed a mean difference (MD) of 24.56 (95% CI 8.97 to 40.15) for evening peak flow. The morning peak flow showed no significant difference (MD 13.59; 95% CI -2.66 to 29.84). The p-value was < 0.05 for the primary outcome.

Authors' conclusions
There is limited evidence to support the use of dehumidification in the home environment for patients with asthma."""
    )


@pytest.fixture
def sample_cleaned_content():
    """Create sample cleaned content for testing."""
    return CleanedContent(
        title="Dehumidifiers for chronic asthma",
        abstract="Humidity control measures in the home environment of patients with asthma have been recommended, since a warm humid environment favours the growth of house dust mites. However, there is no consensus about the usefulness of these measures.",
        full_content="Full content about dehumidification and asthma treatment",
        authors=["Dr. Medical Author", "Dr. Another Author"],
        doi="10.1002/14651858.CD000001.pub1",
        topic_name="Allergy & intolerance",
        quality_grade=QualityGrade.A
    )


@pytest.fixture
def sample_extracted_sections():
    """Create sample extracted sections for testing."""
    sections = {
        "abstract": SectionContent(
            name="abstract",
            content="Humidity control measures in the home environment of patients with asthma have been recommended.",
            subsections={
                "background": "Humidity control measures in the home environment of patients with asthma have been recommended, since a warm humid environment favours the growth of house dust mites.",
                "objectives": "To study the effect of dehumidification of the home environment on asthma control.",
                "main_results": "The trial showed a mean difference (MD) of 24.56 (95% CI 8.97 to 40.15) for evening peak flow.",
                "authors_conclusions": "There is limited evidence to support the use of dehumidification in the home environment for patients with asthma."
            }
        ),
        "background": SectionContent(
            name="background",
            content="Humidity control measures in the home environment of patients with asthma have been recommended, since a warm humid environment favours the growth of house dust mites. However, there is no consensus about the usefulness of these measures."
        ),
        "objectives": SectionContent(
            name="objectives",
            content="To study the effect of dehumidification of the home environment on asthma control."
        ),
        "results": SectionContent(
            name="results",
            content="The trial showed a mean difference (MD) of 24.56 (95% CI 8.97 to 40.15) for evening peak flow. The morning peak flow showed no significant difference (MD 13.59; 95% CI -2.66 to 29.84)."
        )
    }
    
    return ExtractedSections(
        sections=sections,
        section_count=len(sections),
        subsection_count=4
    )


@pytest.fixture
def sample_pico_elements():
    """Create sample PICO elements for testing."""
    return PicoElements(
        population=["adults with asthma", "children with asthma", "patients with house dust mite allergy"],
        intervention=["dehumidification", "mechanical ventilation", "high efficiency vacuum cleaner"],
        comparison=["placebo", "no treatment", "sham intervention"],
        outcome=["evening peak flow", "morning peak flow", "asthma control", "quality of life"]
    )




@pytest.fixture
def sample_medical_entities():
    """Create sample medical entities for testing."""
    return MedicalEntities(
        conditions=["asthma", "house dust mite allergy", "chronic asthma"],
        drugs=["antihistamine", "corticosteroid"],
        procedures=["dehumidification", "mechanical ventilation", "vacuum cleaning"],
        outcomes=["peak flow", "asthma control", "quality of life", "exacerbation"]
    )


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    json_content = {
        "url": "https://example.com",
        "number": 1,
        "timestamp": 1234567890.0,
        "title": "Test Title",
        "doi": "10.1002/test",
        "abstract": "Test abstract",
        "authors": ["Author One"],
        "topic_name": "Test Topic",
        "topic_page": 1,
        "quality": {"grade": "A"}
    }
    
    json_file = temp_dir / "test.json"
    import json
    with open(json_file, 'w') as f:
        json.dump(json_content, f)
    
    return json_file


@pytest.fixture
def sample_invalid_json_file(temp_dir):
    """Create a sample invalid JSON file for testing."""
    json_file = temp_dir / "invalid.json"
    with open(json_file, 'w') as f:
        f.write("invalid json content")
    
    return json_file


@pytest.fixture
def sample_large_json_file(temp_dir):
    """Create a sample large JSON file for testing."""
    json_content = {
        "url": "https://example.com",
        "number": 1,
        "timestamp": 1234567890.0,
        "title": "Large Test Title",
        "doi": "10.1002/large_test",
        "abstract": "Large test abstract with lots of content",
        "authors": ["Author One", "Author Two", "Author Three"],
        "topic_name": "Large Test Topic",
        "topic_page": 1,
        "quality": {"grade": "A"},
        "full_content": "Very long content " * 1000  # Simulate large content
    }
    
    json_file = temp_dir / "large_test.json"
    import json
    with open(json_file, 'w') as f:
        json.dump(json_content, f)
    
    return json_file


@pytest.fixture
def mock_processing_pipeline():
    """Create a mock processing pipeline for testing."""
    from unittest.mock import Mock
    from src.core.data_models import ProcessingResult, ProcessedDocument
    
    mock_pipeline = Mock()
    mock_pipeline.process_document.return_value = ProcessingResult(
        success=True,
        document=ProcessedDocument(
            metadata=Mock(),
            sections=Mock()
        ),
        processing_time=1.0
    )
    
    return mock_pipeline


@pytest.fixture
def mock_file_validator():
    """Create a mock file validator for testing."""
    from unittest.mock import Mock
    from src.core.data_models import ValidationResult
    
    mock_validator = Mock()
    mock_validator.validate_file.return_value = ValidationResult(is_valid=True)
    
    return mock_validator


@pytest.fixture
def mock_content_cleaner():
    """Create a mock content cleaner for testing."""
    from unittest.mock import Mock
    
    mock_cleaner = Mock()
    mock_cleaner.clean_content.return_value = Mock()
    
    return mock_cleaner


@pytest.fixture
def mock_section_extractor():
    """Create a mock section extractor for testing."""
    from unittest.mock import Mock
    
    mock_extractor = Mock()
    mock_extractor.extract_sections.return_value = Mock()
    
    return mock_extractor


@pytest.fixture
def mock_pico_extractor():
    """Create a mock PICO extractor for testing."""
    from unittest.mock import Mock
    
    mock_extractor = Mock()
    mock_extractor.extract_pico_elements.return_value = Mock()
    
    return mock_extractor




@pytest.fixture
def mock_metadata_enricher():
    """Create a mock metadata enricher for testing."""
    from unittest.mock import Mock
    
    mock_enricher = Mock()
    mock_enricher.enrich_metadata.return_value = Mock()
    
    return mock_enricher


@pytest.fixture
def mock_quality_validator():
    """Create a mock quality validator for testing."""
    from unittest.mock import Mock
    
    mock_validator = Mock()
    mock_validator.validate_document_quality.return_value = True
    
    return mock_validator


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add slow marker to tests that might take longer
        if "large" in item.name or "batch" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to tests that test multiple components
        if "pipeline" in item.name or "main" in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to individual component tests
        if any(component in item.name for component in ["validator", "cleaner", "extractor", "parser", "enricher"]):
            item.add_marker(pytest.mark.unit)
