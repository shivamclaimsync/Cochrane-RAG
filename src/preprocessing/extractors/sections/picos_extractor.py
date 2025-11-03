"""
PICOs section extractor.
Extracts the PICOs section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class PicosExtractor(BaseSectionExtractor):
    """Extracts the PICOs section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "picos"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract PICOs section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find PICOs section start
        start_pos = self._find_section_start(cleaned_content, "PICOs")
        if start_pos is None:
            return None
        
        # Extract the full PICOs section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "PICOs")
        
        # Remove the "PICOs" header from the content
        section_content = section_text
        picos_header_pattern = r'^PICOs\s*\n'
        section_content = re.sub(picos_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_picos_subsections(section_content)
        
        return SectionContent(
            name="picos",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_picos_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all PICOs subsections.
        
        Args:
            section_text: Text of the PICOs section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = ['population', 'intervention', 'comparison', 'outcome']
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            content = self._extract_picos_subsection_content(section_text, subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
    
    def _extract_picos_subsection_content(self, section_text: str, subsection_name: str, 
                                        next_subsection_names: list = None) -> Optional[str]:
        """
        Extract content for a specific PICOs subsection.
        
        Args:
            section_text: Text of the PICOs section
            subsection_name: Name of the subsection to extract
            next_subsection_names: List of possible next subsection names
            
        Returns:
            Subsection content if found, None otherwise
        """
        # Create pattern for the subsection (PICOs subsections often have parentheses)
        patterns = [
            rf'^{re.escape(subsection_name)}\s*\([^)]*\)\s*\n',
            rf'^{re.escape(subsection_name)}\s*\n',
            rf'{re.escape(subsection_name)}\s*\([^)]*\)\s*\n[A-Z]',
            rf'{re.escape(subsection_name)}\s*\n[A-Z]'
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, section_text, re.MULTILINE | re.IGNORECASE)
            if match:
                break
        
        if not match:
            return None
        
        start_pos = match.end()
        
        # Find end position
        end_pos = len(section_text)
        
        if next_subsection_names:
            for next_subsection in next_subsection_names:
                next_patterns = [
                    rf'^{re.escape(next_subsection)}\s*\([^)]*\)\s*\n',
                    rf'^{re.escape(next_subsection)}\s*\n',
                    rf'{re.escape(next_subsection)}\s*\([^)]*\)\s*\n[A-Z]',
                    rf'{re.escape(next_subsection)}\s*\n[A-Z]'
                ]
                
                for next_pattern in next_patterns:
                    next_match = re.search(next_pattern, section_text[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if next_match:
                        potential_end = start_pos + next_match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        return section_text[start_pos:end_pos].strip()
