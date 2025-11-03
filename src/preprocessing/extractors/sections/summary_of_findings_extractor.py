"""
Summary of Findings section extractor.
Extracts the Summary of Findings section with structured table data according to Cochrane format.
"""

import re
from typing import Optional, Dict
from ..base_section_extractor import BaseSectionExtractor
from src.core.data_models import SectionContent


class SummaryOfFindingsExtractor(BaseSectionExtractor):
    """Extracts the Summary of Findings section with structured table data."""
    
    def get_section_name(self) -> str:
        return "summary_of_findings"
    
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract Summary of Findings section.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        # Clean content first
        cleaned_content = self._clean_content(content)
        
        # Find Summary of Findings section start
        start_pos = self._find_section_start(cleaned_content, "Summary of findings")
        if start_pos is None:
            return None
        
        # Extract the full Summary of Findings section
        section_text = self._extract_until_next_section(cleaned_content, start_pos, "Summary of findings")
        
        # Remove the "Summary of findings" header from the content
        section_content = section_text
        sof_header_pattern = r'^Summary of findings\s*\n'
        section_content = re.sub(sof_header_pattern, '', section_content, flags=re.MULTILINE | re.IGNORECASE)
        section_content = section_content.strip()
        
        if len(section_content) < 50:
            return None
        
        # Extract subsections (structured table data)
        subsections = self._extract_sof_subsections(section_content)
        
        return SectionContent(
            name="summary_of_findings",
            content=section_content,
            subsections=subsections
        )
    
    def _extract_sof_subsections(self, section_text: str) -> Dict[str, str]:
        """
        Extract Summary of Findings subsections (structured table data).
        
        Args:
            section_text: Text of the Summary of Findings section
            
        Returns:
            Dictionary of subsection names to content
        """
        subsections = {}
        
        # Extract individual comparison tables
        comparison_patterns = [
            r'Summary of findings for the main comparison\.\s*(.*?)(?=\n(?:Summary of findings \d+|Background|$))',
            r'Summary of findings \d+\.\s*(.*?)(?=\n(?:Summary of findings \d+|Background|$))',
            r'Open in table viewer\s*(.*?)(?=\n(?:Open in table viewer|Background|$))'
        ]
        
        for i, pattern in enumerate(comparison_patterns):
            matches = re.finditer(pattern, section_text, re.DOTALL | re.IGNORECASE)
            for j, match in enumerate(matches):
                subsection_name = f"comparison_{i+1}_{j+1}" if j > 0 else f"comparison_{i+1}"
                content = match.group(1).strip()
                if content and len(content) > 20:
                    subsections[subsection_name] = content
        
        # If no structured tables found, try to extract any table-like content
        if not subsections:
            # Look for table content patterns
            table_patterns = [
                r'Patient or population:.*?(?=\n(?:Background|$))',
                r'Setting:.*?(?=\n(?:Background|$))',
                r'Intervention:.*?(?=\n(?:Background|$))',
                r'Comparison:.*?(?=\n(?:Background|$))',
                r'Outcomes\s*\n.*?(?=\n(?:Background|$))'
            ]
            
            for i, pattern in enumerate(table_patterns):
                match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(0).strip()
                    if content and len(content) > 20:
                        subsections[f"table_content_{i+1}"] = content
        
        return subsections
