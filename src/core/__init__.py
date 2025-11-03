"""
Core module for shared data models and utilities.

This module contains the fundamental data structures and utilities
used across all other modules in the RAG system.
"""

from .data_models import (
    QualityGrade, StudyDesign, RawCochraneData, ValidationResult,
    CleanedContent, SectionContent, ExtractedSections, PicoElements,
    MedicalEntities, EnrichedMetadata, ProcessedDocument,
    ProcessingResult, ProcessingStats
)

__all__ = [
    'QualityGrade', 'StudyDesign', 'RawCochraneData', 'ValidationResult',
    'CleanedContent', 'SectionContent', 'ExtractedSections', 'PicoElements',
    'MedicalEntities', 'EnrichedMetadata', 'ProcessedDocument',
    'ProcessingResult', 'ProcessingStats'
]
