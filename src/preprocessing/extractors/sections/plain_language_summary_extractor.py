"""
Plain Language Summary section extractor.
Extracts the Plain Language Summary section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class PlainLanguageSummaryExtractor(BaseSectionExtractor):
    """Extracts the Plain Language Summary section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "plain_language_summary"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Plain Language Summary section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Plain Language Summary section start
        start_pos = self._find_section_start(cleaned_content, "Plain language summary")
        if start_pos is None:
            return None
        
        # Extract the full Plain Language Summary section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Plain language summary")
        
        # Remove the "Plain language summary" header from the content
        section_content = section_text
        pls_header_pattern = r'^Plain language summary\s*\n(?:available in\s*\n)?'
        section_content = re.sub(pls_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_pls_subsections(section_content)
        
        return SectionContent(
            name="plain_language_summary",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_pls_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Plain Language Summary subsections.
        
        Args:
            section_text: Text of the Plain Language Summary section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = [
            'available_in',
            'review_question',
            'background',
            'search_date',
            'study_characteristics',
            'key_results',
            'authors_conclusions',
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
