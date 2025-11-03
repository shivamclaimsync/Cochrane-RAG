"""
Refactored section extractor using individual section extractors.
Provides comprehensive extraction of all Cochrane sections and subsections.
"""

import re
from typing import Dict
from src.core.data_models import CleanedContent, ExtractedSections, SectionContent

# Import all section extractors
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


class RefactoredSectionExtractor:
    """Refactored section extractor using individual section extractors."""
    
    def __init__(self):
        """Initialize all section extractors."""
        self.extractors = [
            AbstractExtractor(),
            PicosExtractor(),
            PlainLanguageSummaryExtractor(),
            SummaryOfFindingsExtractor(),
            AuthorsConclusionsExtractor(),
            BackgroundExtractor(),
            ObjectivesExtractor(),
            MethodsExtractor(),
            ResultsExtractor(),
            DiscussionExtractor()
        ]
    
    def extract_sections(self, content_input) -> ExtractedSections:
        """
        Extract all sections using specialized extractors.
        
        Args:
            content_input: Either CleanedContent object or string content to extract sections from
            
        Returns:
            ExtractedSections with complete hierarchical structure
        """
        sections = {}
        total_subsections = 0
        
        # Handle both CleanedContent objects and string input
        if isinstance(content_input, str):
            content_to_extract = self._extract_actual_content_from_full(content_input)
        else:
            # Determine content to extract
            content_to_extract = content_input.abstract or content_input.full_content
            
            # If we're using full_content, clean it first
            if not content_input.abstract and content_input.full_content:
                content_to_extract = self._extract_actual_content_from_full(content_input.full_content)
        
        # Extract each section using specialized extractors
        for extractor in self.extractors:
            try:
                section_content = extractor.extract(content_to_extract)
                if section_content:
                    sections[extractor.get_section_name()] = section_content
                    total_subsections += len(section_content.subsections)
            except Exception as e:
                # Log error but continue with other extractors
                print(f"Error extracting {extractor.get_section_name()}: {e}")
                continue
        
        return ExtractedSections(
            sections=sections,
            section_count=len(sections),
            subsection_count=total_subsections
        )
    
    def _extract_actual_content_from_full(self, full_content: str) -> str:
        """
        Extract actual content from full_content that may contain navigation elements.
        
        Args:
            full_content: Raw full content from the JSON
            
        Returns:
            Cleaned content ready for section extraction
        """
        # Enhanced content extraction logic
        content_start_patterns = [
            r'Cochrane Database of Systematic reviews.*?Review - Intervention',
            r'Review - Intervention.*?Abstract',
            r'Authors\' declarations of interest.*?Abstract',
            r'Abstract\s*\n(?:available in\s*\n)?',
            r'Background\s*\n(?:available in\s*\n)?',
            r'PICOs\s*\n',
            r'Plain language summary\s*\n(?:available in\s*\n)?',
            r'Authors\' conclusions\s*\n(?:available in\s*\n)?'
        ]
        
        content_start = 0
        for pattern in content_start_patterns:
            match = re.search(pattern, full_content, re.DOTALL | re.IGNORECASE)
            if match:
                content_start = match.start()
                break
        
        if content_start == 0:
            # Fallback: look for the first section header
            lines = full_content.split('\n')
            section_headers = ['Abstract', 'Background', 'Objectives', 'Methods', 'Results', 'Discussion', 'PICOs', 'Plain language summary', 'Authors\' conclusions', 'Summary of findings']
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                # Look for section headers first
                if line_stripped in section_headers:
                    content_start = sum(len(lines[j]) + 1 for j in range(i))
                    break
                # If no section headers found, look for substantial text
                elif len(line_stripped) > 50 and not line_stripped.startswith(('Skip to', 'Trusted evidence', 'Basic Search', 'Sign In')):
                    content_start = sum(len(lines[j]) + 1 for j in range(i))
                    break
        
        # Extract content from the start position
        content = full_content[content_start:]
        
        # Remove navigation elements
        navigation_patterns = [
            r'Download PDF.*?Share',
            r'Cite this review.*?Full text views:.*?\d+',
            r'Contents\s*\n.*?Related\n',
            r'Cochrane Clinical Answers.*?Request data reuse',
            r'Browse Publications.*?Cookie Preferences',
            r'Copyright ©.*?Cookie Preferences',
            r'Unlock the full review.*?Cookie P',
            r'Skip to Content.*?Sign In',
            r'Trusted evidence.*?Basic Search',
            r'Cookie Preferences.*?Cookie Preferences',
            r'Request data reuse.*?Request data reuse'
        ]
        
        for pattern in navigation_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n+', '\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def get_extraction_stats(self, sections: Dict[str, SectionContent]) -> Dict[str, int]:
        """
        Get extraction statistics for debugging and analysis.
        
        Args:
            sections: Dictionary of extracted sections
            
        Returns:
            Dictionary with extraction statistics
        """
        stats = {
            'total_sections': len(sections),
            'total_subsections': sum(len(section.subsections) for section in sections.values()),
            'sections_with_subsections': sum(1 for section in sections.values() if section.subsections),
            'sections_extracted': list(sections.keys())
        }
        
        # Add per-section stats
        for section_name, section in sections.items():
            stats[f'{section_name}_subsections'] = len(section.subsections)
            stats[f'{section_name}_content_length'] = len(section.content)
        
        return stats
