"""
Discussion section extractor.
Extracts the Discussion section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class DiscussionExtractor(BaseSectionExtractor):
    """Extracts the Discussion section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "discussion"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Discussion section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Discussion section start
        start_pos = self._find_section_start(cleaned_content, "Discussion")
        if start_pos is None:
            return None
        
        # Extract the full Discussion section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Discussion")
        
        # Remove the "Discussion" header from the content
        section_content = section_text
        discussion_header_pattern = r'^Discussion\s*\n(?:available in\s*\n)?'
        section_content = re.sub(discussion_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_discussion_subsections(section_content)
        
        return SectionContent(
            name="discussion",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_discussion_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Discussion subsections.
        
        Args:
            section_text: Text of the Discussion section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction (using actual subsection names from content)
        subsection_order = [
            'available_in',
            'summary_of_main_results',
            'overall_completeness_and_applicability_of_evidence',
            'quality_of_the_evidence',
            'potential_biases_in_the_review_process',
            'agreements_and_disagreements_with_other_studies_or_reviews'
        ]
        
        # Map subsection names to their actual names in content
        subsection_name_mapping = {
            'available_in': 'available in',
            'summary_of_main_results': 'summary of main results',
            'overall_completeness_and_applicability_of_evidence': 'overall completeness and applicability of evidence',
            'quality_of_the_evidence': 'quality of the evidence',
            'potential_biases_in_the_review_process': 'potential biases in the review process',
            'agreements_and_disagreements_with_other_studies_or_reviews': 'agreements and disagreements with other studies or reviews'
        }
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            # Use the mapped name for extraction
            actual_subsection_name = subsection_name_mapping.get(subsection_name, subsection_name)
            content = self._extract_subsection_content(section_text, actual_subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
