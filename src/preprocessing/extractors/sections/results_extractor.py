"""
Results section extractor.
Extracts the Results section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class ResultsExtractor(BaseSectionExtractor):
    """Extracts the Results section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "results"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Results section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Results section start
        start_pos = self._find_section_start(cleaned_content, "Results")
        if start_pos is None:
            return None
        
        # Extract the full Results section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Results")
        
        # Remove the "Results" header from the content
        section_content = section_text
        results_header_pattern = r'^Results\s*\n'
        section_content = re.sub(results_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_results_subsections(section_content)
        
        return SectionContent(
            name="results",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_results_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Results subsections.
        
        Args:
            section_text: Text of the Results section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = [
            'description_of_studies',
            'results_of_the_search',
            'included_studies',
            'excluded_studies',
            'risk_of_bias_in_included_studies',
            'methodology_characteristics',
            'patient_characteristics',
            'interventions',
            'outcomes',
            'leukoreduction_definition',
            'type_of_filters',
            'control_groups',
            'cointervention'
        ]
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            content = self._extract_subsection_content(section_text, subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
