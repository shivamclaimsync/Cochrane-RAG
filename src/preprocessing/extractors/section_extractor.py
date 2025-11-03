"""
Main section extractor that uses the refactored extraction system.
This is the main entry point for section extraction in the pipeline.
"""

from src.core.data_models import CleanedContent, ExtractedSections
from .refactored_section_extractor import RefactoredSectionExtractor


class SectionExtractor:
    """Main section extractor using the refactored extraction system."""
    
    def __init__(self):
        """Initialize the refactored section extractor."""
        self.refactored_extractor = RefactoredSectionExtractor()
    
    def extract_sections(self, cleaned_content: CleanedContent) -> ExtractedSections:
        """
        Extract hierarchical sections from cleaned content using refactored extractors.

        Args:
            cleaned_content: Cleaned content to extract sections from

        Returns:
            ExtractedSections with hierarchical structure
        """
        return self.refactored_extractor.extract_sections(cleaned_content)
