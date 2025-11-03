"""
Abstract section extractor.
Extracts the Abstract section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class AbstractExtractor(BaseSectionExtractor):
    """Extracts the Abstract section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "abstract"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Abstract section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Abstract section start - try multiple patterns
        start_pos = None
        
        # Pattern 1: Look for "Abstract" followed by "available in"
        abstract_pattern1 = re.search(r'Abstract\s*\n(?:available in\s*\n)?', cleaned_content, re.IGNORECASE)
        if abstract_pattern1:
            start_pos = abstract_pattern1.start()
        else:
            # Pattern 2: Look for "Abstract" at start of line
            abstract_pattern2 = re.search(r'^Abstract\s*\n', cleaned_content, re.MULTILINE | re.IGNORECASE)
            if abstract_pattern2:
                start_pos = abstract_pattern2.start()
            else:
                # Pattern 3: Look for "Abstract" anywhere
                abstract_pattern3 = re.search(r'Abstract\s*\n', cleaned_content, re.IGNORECASE)
                if abstract_pattern3:
                    start_pos = abstract_pattern3.start()
        
        if start_pos is None:
            return None
        
        # For Abstract, we need to find the end manually since it doesn't have clear boundaries
        # Look for the next major section after Abstract (not subsections within Abstract)
        # The Abstract section typically ends with PICOs or Plain language summary
        next_sections = ['PICOs', 'Plain language summary', 'Authors\' conclusions', 'Summary of findings']
        
        end_pos = len(cleaned_content)
        for next_section in next_sections:
            # Look for the next section header - try multiple patterns
            patterns = [
                rf'\n{re.escape(next_section)}\s*\n',
                rf'\n{re.escape(next_section)}\s*\n(?:available in\s*\n)?',
                rf'\n{re.escape(next_section)}\s*\n[A-Z]',
                rf'\n{re.escape(next_section)}[:\s]*[A-Z]'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, cleaned_content[start_pos:], re.MULTILINE | re.IGNORECASE)
                if match:
                    potential_end = start_pos + match.start()
                    if potential_end < end_pos:
                        end_pos = potential_end
                    break
        
        # Extract the full Abstract section
        section_text = cleaned_content[start_pos:end_pos].strip()
        
        # Remove the "Abstract" header from the content
        section_content = section_text
        abstract_header_pattern = r'^Abstract\s*\n(?:available in\s*\n)?'
        section_content = re.sub(abstract_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_abstract_subsections(section_content)
        
        return SectionContent(
            name="abstract",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_abstract_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Abstract subsections.
        
        Args:
            section_text: Text of the Abstract section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = [
            'available_in',
            'background', 
            'objectives',
            'search_methods',
            'selection_criteria',
            'data_collection_and_analysis',
            'main_results',
            'authors_conclusions'
        ]
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            content = self._extract_subsection_content(section_text, subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
