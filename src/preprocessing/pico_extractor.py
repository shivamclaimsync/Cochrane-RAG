"""
PICO element extraction component for Cochrane RAG system.

This module handles extraction of Population, Intervention, Comparison, and Outcome
elements from Cochrane content, following single responsibility principle.
"""

import re
from typing import List, Dict, Any
from src.core.data_models import ExtractedSections, PicoElements


class PicoExtractor:
    """Extracts PICO elements from extracted sections."""
    
    # Enhanced patterns for identifying PICO elements
    POPULATION_PATTERNS = [
        r'population\s*\([^)]*\)',
        r'patients?\s+with\s+[^.]*',
        r'participants?\s+with\s+[^.]*',
        r'adults?\s+with\s+[^.]*',
        r'children?\s+with\s+[^.]*',
        r'aged\s+\d+',
        r'elderly\s+patients?',
        r'pregnant\s+women',
        r'patients?\s+diagnosed\s+with',
        r'individuals?\s+with\s+[^.]*',
        r'people\s+with\s+[^.]*',
        r'women\s+with\s+[^.]*',
        r'men\s+with\s+[^.]*',
        r'infants?\s+with\s+[^.]*',
        r'neonates?\s+with\s+[^.]*',
        r'critically\s+ill\s+patients?',
        r'hospitalized\s+patients?',
        r'outpatients?',
        r'emergency\s+department\s+patients?'
    ]
    
    INTERVENTION_PATTERNS = [
        r'intervention\s*\([^)]*\)',
        r'treatment\s+with\s+[^.]*',
        r'therapy\s+with\s+[^.]*',
        r'administration\s+of\s+[^.]*',
        r'use\s+of\s+[^.]*',
        r'application\s+of\s+[^.]*',
        r'implementation\s+of\s+[^.]*',
        r'provision\s+of\s+[^.]*',
        r'drug\s+therapy',
        r'pharmacological\s+intervention',
        r'surgical\s+intervention',
        r'non-pharmacological\s+intervention',
        r'behavioral\s+intervention',
        r'educational\s+intervention',
        r'exercise\s+intervention',
        r'dietary\s+intervention',
        r'psychological\s+intervention'
    ]
    
    COMPARISON_PATTERNS = [
        r'comparison\s*\([^)]*\)',
        r'compared\s+to\s+[^.]*',
        r'versus\s+[^.]*',
        r'vs\.\s+[^.]*',
        r'placebo\s+[^.]*',
        r'control\s+group',
        r'standard\s+care',
        r'no\s+treatment',
        r'sham\s+[^.]*',
        r'alternative\s+treatment',
        r'conventional\s+treatment',
        r'usual\s+care',
        r'baseline\s+treatment',
        r'active\s+control',
        r'waiting\s+list\s+control'
    ]
    
    OUTCOME_PATTERNS = [
        r'outcome\s*\([^)]*\)',
        r'primary\s+outcome',
        r'secondary\s+outcome',
        r'endpoint',
        r'measure\s+of\s+[^.]*',
        r'assessment\s+of\s+[^.]*',
        r'evaluation\s+of\s+[^.]*',
        r'improvement\s+in\s+[^.]*',
        r'reduction\s+in\s+[^.]*',
        r'change\s+in\s+[^.]*',
        r'mortality',
        r'morbidity',
        r'quality\s+of\s+life',
        r'pain\s+relief',
        r'symptom\s+improvement',
        r'functional\s+outcome',
        r'adverse\s+events',
        r'side\s+effects',
        r'complications',
        r'hospital\s+length\s+of\s+stay',
        r'readmission\s+rate'
    ]
    
    def extract_pico_elements(self, sections: ExtractedSections) -> PicoElements:
        """
        Extract PICO elements from extracted sections.
        
        Args:
            sections: Extracted sections containing content
            
        Returns:
            PicoElements with extracted PICO information
        """
        population = self._extract_population(sections)
        intervention = self._extract_intervention(sections)
        comparison = self._extract_comparison(sections)
        outcome = self._extract_outcome(sections)
        
        return PicoElements(
            population=population,
            intervention=intervention,
            comparison=comparison,
            outcome=outcome
        )
    
    def _extract_population(self, sections: ExtractedSections) -> List[str]:
        """Extract population elements from sections."""
        population_elements = []
        
        # Check PICOs section first (if available)
        if 'picos' in sections.sections:
            picos_content = sections.sections['picos'].content
            population_elements.extend(self._extract_from_picos_section(picos_content, 'population'))
        
        # Check background section (most common for population info)
        if 'background' in sections.sections:
            background_content = sections.sections['background'].content
            population_elements.extend(self._extract_with_patterns(background_content, self.POPULATION_PATTERNS))
        
        # Check methods section (often contains participant criteria)
        if 'methods' in sections.sections:
            methods_content = sections.sections['methods'].content
            population_elements.extend(self._extract_with_patterns(methods_content, self.POPULATION_PATTERNS))
        
        # Check abstract section (if available)
        if 'abstract' in sections.sections:
            abstract_content = sections.sections['abstract'].content
            population_elements.extend(self._extract_with_patterns(abstract_content, self.POPULATION_PATTERNS))
        
        return self._clean_and_deduplicate(population_elements)
    
    def _extract_intervention(self, sections: ExtractedSections) -> List[str]:
        """Extract intervention elements from sections."""
        intervention_elements = []
        
        # Check PICOs section first (if available)
        if 'picos' in sections.sections:
            picos_content = sections.sections['picos'].content
            intervention_elements.extend(self._extract_from_picos_section(picos_content, 'intervention'))
        
        # Check methods section (often contains intervention details)
        if 'methods' in sections.sections:
            methods_content = sections.sections['methods'].content
            intervention_elements.extend(self._extract_with_patterns(methods_content, self.INTERVENTION_PATTERNS))
        
        # Check background section (intervention description)
        if 'background' in sections.sections:
            background_content = sections.sections['background'].content
            intervention_elements.extend(self._extract_with_patterns(background_content, self.INTERVENTION_PATTERNS))
        
        # Check abstract section (if available)
        if 'abstract' in sections.sections:
            abstract_content = sections.sections['abstract'].content
            intervention_elements.extend(self._extract_with_patterns(abstract_content, self.INTERVENTION_PATTERNS))
        
        return self._clean_and_deduplicate(intervention_elements)
    
    def _extract_comparison(self, sections: ExtractedSections) -> List[str]:
        """Extract comparison elements from sections."""
        comparison_elements = []
        
        # Check PICOs section first (if available)
        if 'picos' in sections.sections:
            picos_content = sections.sections['picos'].content
            comparison_elements.extend(self._extract_from_picos_section(picos_content, 'comparison'))
        
        # Check methods section (often contains comparison details)
        if 'methods' in sections.sections:
            methods_content = sections.sections['methods'].content
            comparison_elements.extend(self._extract_with_patterns(methods_content, self.COMPARISON_PATTERNS))
        
        # Check background section (comparison description)
        if 'background' in sections.sections:
            background_content = sections.sections['background'].content
            comparison_elements.extend(self._extract_with_patterns(background_content, self.COMPARISON_PATTERNS))
        
        # Check abstract section (if available)
        if 'abstract' in sections.sections:
            abstract_content = sections.sections['abstract'].content
            comparison_elements.extend(self._extract_with_patterns(abstract_content, self.COMPARISON_PATTERNS))
        
        return self._clean_and_deduplicate(comparison_elements)
    
    def _extract_outcome(self, sections: ExtractedSections) -> List[str]:
        """Extract outcome elements from sections."""
        outcome_elements = []
        
        # Check PICOs section first (if available)
        if 'picos' in sections.sections:
            picos_content = sections.sections['picos'].content
            outcome_elements.extend(self._extract_from_picos_section(picos_content, 'outcome'))
        
        # Check methods section (often contains outcome measures)
        if 'methods' in sections.sections:
            methods_content = sections.sections['methods'].content
            outcome_elements.extend(self._extract_with_patterns(methods_content, self.OUTCOME_PATTERNS))
        
        # Check results section (outcome results)
        if 'results' in sections.sections:
            results_content = sections.sections['results'].content
            outcome_elements.extend(self._extract_with_patterns(results_content, self.OUTCOME_PATTERNS))
        
        # Check background section (outcome description)
        if 'background' in sections.sections:
            background_content = sections.sections['background'].content
            outcome_elements.extend(self._extract_with_patterns(background_content, self.OUTCOME_PATTERNS))
        
        # Check abstract section (if available)
        if 'abstract' in sections.sections:
            abstract_content = sections.sections['abstract'].content
            outcome_elements.extend(self._extract_with_patterns(abstract_content, self.OUTCOME_PATTERNS))
        
        return self._clean_and_deduplicate(outcome_elements)
    
    def _extract_from_picos_section(self, content: str, pico_type: str) -> List[str]:
        """Extract PICO elements from a structured PICOs section."""
        elements = []
        
        # Look for specific PICO type in the content
        pattern = re.compile(rf'{pico_type}\s*\([^)]*\)', re.IGNORECASE)
        matches = pattern.findall(content)
        
        for match in matches:
            # Extract content within parentheses
            inner_content = re.search(r'\(([^)]*)\)', match)
            if inner_content:
                elements.append(inner_content.group(1).strip())
        
        return elements
    
    def _extract_with_patterns(self, content: str, patterns: List[str]) -> List[str]:
        """Extract elements using regex patterns."""
        elements = []
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    # If pattern has groups, take the first non-empty group
                    element = next((group for group in match if group.strip()), '')
                else:
                    element = match
                
                if element and len(element.strip()) > 5:  # Minimum length filter
                    elements.append(element.strip())
        
        return elements
    
    def _clean_and_deduplicate(self, elements: List[str]) -> List[str]:
        """Clean and deduplicate extracted elements."""
        if not elements:
            return []
        
        # Clean elements
        cleaned = []
        for element in elements:
            # Remove extra whitespace
            cleaned_element = re.sub(r'\s+', ' ', element.strip())
            
            # Remove common prefixes/suffixes
            cleaned_element = re.sub(r'^(the|a|an)\s+', '', cleaned_element, flags=re.IGNORECASE)
            cleaned_element = re.sub(r'\s+(and|or|but)\s*$', '', cleaned_element, flags=re.IGNORECASE)
            
            # Minimum length check
            if len(cleaned_element) > 5:
                cleaned.append(cleaned_element)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for element in cleaned:
            if element.lower() not in seen:
                seen.add(element.lower())
                unique_elements.append(element)
        
        return unique_elements[:10]  # Limit to 10 elements per category