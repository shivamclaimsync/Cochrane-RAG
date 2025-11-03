"""
Background section extractor.
Extracts the Background section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class BackgroundExtractor(BaseSectionExtractor):
    """Extracts the Background section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "background"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Background section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Background section start
        start_pos = self._find_section_start(cleaned_content, "Background")
        if start_pos is None:
            return None
        
        # Extract the full Background section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Background")
        
        # Remove the "Background" header from the content
        section_content = section_text
        background_header_pattern = r'^Background\s*\n(?:available in\s*\n)?'
        section_content = re.sub(background_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_background_subsections(section_content)
        
        return SectionContent(
            name="background",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_background_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Background subsections.
        
        Args:
            section_text: Text of the Background section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = [
            'available_in',
            'description_of_the_condition',
            'description_of_the_intervention',
            'how_the_intervention_might_work',
            'why_it_is_important_to_do_this_review'
        ]
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            content = self._extract_subsection_content(section_text, subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
