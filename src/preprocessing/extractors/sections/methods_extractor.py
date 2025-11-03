"""
Methods section extractor.
Extracts the Methods section with all its subsections according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class MethodsExtractor(BaseSectionExtractor):
    """Extracts the Methods section with all its subsections."""
    
    def get_section_name(self) -> str:
        return "methods"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Methods section with subsections.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Methods section start
        start_pos = self._find_section_start(cleaned_content, "Methods")
        if start_pos is None:
            return None
        
        # Extract the full Methods section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Methods")
        
        # Remove the "Methods" header from the content
        section_content = section_text
        methods_header_pattern = r'^Methods\s*\n(?:available in\s*\n)?'
        section_content = re.sub(methods_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections
        subsections = self._extract_methods_subsections(section_content)
        
        return SectionContent(
            name="methods",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_methods_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract all Methods subsections.
        
        Args:
            section_text: Text of the Methods section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Define subsection order for proper extraction
        subsection_order = [
            'available_in',
            'criteria_for_considering_studies_for_this_review',
            'search_methods_for_identification_of_studies',
            'data_collection_and_analysis',
            'selection_of_studies',
            'data_extraction_and_management',
            'assessment_of_risk_of_bias_in_included_studies',
            'measures_of_treatment_effect',
            'unit_of_analysis_issues',
            'dealing_with_missing_data',
            'assessment_of_heterogeneity',
            'assessment_of_reporting_biases',
            'data_synthesis',
            'subgroup_analysis_and_investigation_of_heterogeneity',
            'sensitivity_analysis',
            'trial_sequential_analysis',
            'summary_of_findings_tables'
        ]
        
        # Extract each subsection
        for i, subsection_name in enumerate(subsection_order):
            next_subsections = subsection_order[i+1:] if i < len(subsection_order) - 1 else []
            
            content = self._extract_subsection_content(section_text, subsection_name, next_subsections)
            if content and len(content) > 10:
                subsections[subsection_name] = content
        
        return subsections
