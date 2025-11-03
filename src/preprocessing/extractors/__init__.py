"""
Section extractors module.
Provides comprehensive section extraction for Cochrane reviews.
"""

from .section_extractor import SectionExtractor
from .refactored_section_extractor import RefactoredSectionExtractor
from .base_section_extractor import BaseSectionExtractor

# Import individual section extractors
from .sections import (
    AbstractExtractor,
    PicosExtractor,
    PlainLanguageSummaryExtractor,
    SummaryOfFindingsExtractor,
    AuthorsConclusionsExtractor,
    BackgroundExtractor,
    ObjectivesExtractor,
    MethodsExtractor,
    ResultsExtractor,
    DiscussionExtractor
)

__all__ = [
    'SectionExtractor',
    'RefactoredSectionExtractor',
    'BaseSectionExtractor',
    'AbstractExtractor',
    'PicosExtractor',
    'PlainLanguageSummaryExtractor',
    'SummaryOfFindingsExtractor',
    'AuthorsConclusionsExtractor',
    'BackgroundExtractor',
    'ObjectivesExtractor',
    'MethodsExtractor',
    'ResultsExtractor',
    'DiscussionExtractor'
]