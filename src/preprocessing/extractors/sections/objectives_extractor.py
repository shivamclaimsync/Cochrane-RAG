"""
Objectives section extractor.
Extracts the Objectives section (standalone section with no subsections) according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class ObjectivesExtractor(BaseSectionExtractor):
    """Extracts the Objectives section (standalone section)."""
    
    def get_section_name(self) -> str:
        return "objectives"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Objectives section.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Objectives section start
        start_pos = self._find_section_start(cleaned_content, "Objectives")
        if start_pos is None:
            return None
        
        # Extract the full Objectives section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Objectives")
        
        # Remove the "Objectives" header from the content
        section_content = section_text
        objectives_header_pattern = r'^Objectives\s*\n'
        section_content = re.sub(objectives_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        # Objectives should only be a single sentence or a few sentences
        # If we extracted too much (e.g., > 500 chars), look for sentence boundary
        if len(section_content) > 500:
            # Try to find where the Objectives sentence ends (period followed by newline and capital letter or section header)
            sentence_end = re.search(r'\.\s*\n(?=[A-Z][a-z]|Summary|Background|Methods|Results|Discussion|Authors)', section_content)
            if sentence_end:
                section_content = section_content[:sentence_end.end() - 1].strip()
        
        if len(section_content) < 50:
            return None
        
        # Objectives is a standalone section with no subsections
        return SectionContent(
            name="objectives",
            content=section_content,
            subsections={}
        )
