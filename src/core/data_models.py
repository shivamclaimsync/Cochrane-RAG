"""
Data models for Cochrane RAG system preprocessing pipeline.

This module defines the data structures used throughout the preprocessing pipeline,
following clean code principles and single responsibility principle.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class QualityGrade(Enum):
    """Quality grade enumeration for Cochrane reviews."""
    A = "A"
    B = "B"
    C = "C"


class StudyDesign(Enum):
    """Study design types."""
    SYSTEMATIC_REVIEW = "systematic_review"
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    OBSERVATIONAL_STUDY = "observational_study"
    META_ANALYSIS = "meta_analysis"


@dataclass
class RawCochraneData:
    """Raw input data from Cochrane JSON files."""
    url: str
    number: int
    timestamp: float
    title: str
    doi: str
    abstract: str
    authors: List[str]
    topic_name: str
    topic_page: int
    quality: Dict[str, Any]
    full_content: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CleanedContent:
    """Content after cleaning and standardization."""
    title: str
    abstract: str
    full_content: str
    authors: List[str]
    doi: str
    topic_name: str
    quality_grade: QualityGrade
    url: str = ''


@dataclass
class SectionContent:
    """Individual section content."""
    name: str
    content: str
    subsections: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExtractedSections:
    """Hierarchically extracted sections."""
    sections: Dict[str, SectionContent] = field(default_factory=dict)
    section_count: int = 0
    subsection_count: int = 0


@dataclass
class PicoElements:
    """PICO elements extracted from content."""
    population: List[str] = field(default_factory=list)
    intervention: List[str] = field(default_factory=list)
    comparison: List[str] = field(default_factory=list)
    outcome: List[str] = field(default_factory=list)




@dataclass
class MedicalEntities:
    """Medical entities extracted from content."""
    conditions: List[str] = field(default_factory=list)
    drugs: List[str] = field(default_factory=list)
    procedures: List[str] = field(default_factory=list)
    outcomes: List[str] = field(default_factory=list)


@dataclass
class EnrichedMetadata:
    """Enhanced metadata for processed content."""
    source_file: str
    title: str
    doi: str
    authors: List[str]
    url: str
    topic_name: str
    quality_grade: QualityGrade
    extraction_date: str
    publication_date: str
    content_length: int
    pico_elements: PicoElements
    medical_entities: MedicalEntities
    sections_extracted: List[str]
    section_count: int
    subsection_count: int
    full_content: Optional[str] = None


@dataclass
class ProcessedDocument:
    """Final processed document structure."""
    metadata: EnrichedMetadata
    sections: ExtractedSections


@dataclass
class ProcessingResult:
    """Result of document processing."""
    success: bool
    document: Optional[ProcessedDocument] = None
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0


@dataclass
class ProcessingStats:
    """Processing statistics."""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_sections: int = 0
    total_subsections: int = 0
