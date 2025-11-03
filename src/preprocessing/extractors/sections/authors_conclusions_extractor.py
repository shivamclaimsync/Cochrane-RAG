"""
Authors' Conclusions section extractor.
Extracts the Authors' Conclusions section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class AuthorsConclusionsExtractor(BaseSectionExtractor):
    """Extracts the Authors' Conclusions section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "authors_conclusions"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Authors' Conclusions section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Authors' Conclusions section start
        start_pos = self._find_section_start(cleaned_content, "Authors' conclusions")
        if start_pos is None:
            return None
        
        # Extract the full Authors' Conclusions section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Authors' conclusions")
        
        # Remove the "Authors' conclusions" header from the content
        section_content = section_text
        conclusions_header_pattern = r'^Authors\' conclusions\s*\n(?:available in\s*\n)?'
        section_content = re.sub(conclusions_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_conclusions_subsections(section_content)
        
        return SectionContent(
            name="authors_conclusions",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_conclusions_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Authors' Conclusions subsections.
        
        Args:
            section_text: Text of the Authors' Conclusions section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = [
            'available_in',
            'implications_for_practice',
            'implications_for_research'
        ]
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            content = self._extract_subsection_content(section_text, subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
