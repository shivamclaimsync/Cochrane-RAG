"""
Base section extractor interface for all section extractors.
Provides common functionality and defines the contract for section extraction.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import re
from src.core.data_models import SectionContent


class BaseSectionExtractor(ABC):
    """Base class for all section extractors."""
    
    @abstractmethod
    def extract(self, content: str) -> Optional[SectionContent]:
        """
        Extract the section from content.
        
        Args:
            content: Full content to extract from
            
        Returns:
            SectionContent if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_section_name(self) -> str:
        """
        Get the name of the section this extractor handles.
        
        Returns:
            Section name string
        """
        pass
    
    def _clean_content(self, content: str) -> str:
        """
        Clean content by removing navigation elements and normalizing.
        
        Args:
            content: Raw content to clean
            
        Returns:
            Cleaned content
        """
        # Remove common navigation elements
        navigation_patterns = [
            r'Download PDF.*?Share',
            r'Cite this review.*?Full text views:.*?\d+',
            r'Contents\s*\n.*?Related\n',
            r'Cochrane Clinical Answers.*?Request data reuse',
            r'Browse Publications.*?Cookie Preferences',
            r'Copyright ©.*?Cookie Preferences',
            r'Skip to.*?Sign In',
            r'Trusted evidence.*?Basic Search',
            r'Unlock the full review.*?Cookie P'
        ]
        
        cleaned = content
        for pattern in navigation_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Normalize whitespace
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _find_section_start(self, content: str, section_name: str) -> Optional[int]:
        """
        Find the start position of a section in content.

        Args:
            content: Content to search in
            section_name: Name of the section to find

        Returns:
            Start position if found, None otherwise
        """
        # Enhanced patterns for better section detection
        patterns = [
            # Standard patterns
            rf'^{re.escape(section_name)}\s*\n',
            rf'{re.escape(section_name)}\s*\n(?:available in\s*\n)?',
            rf'{re.escape(section_name)}\s*\n[A-Z]',
            rf'{re.escape(section_name)}[:\s]*[A-Z]',
            # Additional patterns for better coverage
            rf'\n{re.escape(section_name)}\s*\n',
            rf'\n{re.escape(section_name)}\s*\n(?:available in\s*\n)?',
            rf'\n{re.escape(section_name)}\s*\n[A-Z]',
            rf'\n{re.escape(section_name)}[:\s]*[A-Z]',
            # Pattern for sections that might be followed by specific text
            rf'{re.escape(section_name)}\s*\n(?:available in\s*\n)?(?:English|Español|Français)',
            # Pattern for sections that might have extra whitespace
            rf'{re.escape(section_name)}\s+\n',
            rf'\n{re.escape(section_name)}\s+\n'
        ]

        # For Plain Language Summary, look for the one with "available in" - this is the actual content section
        if section_name.lower() == 'plain language summary':
            # Look for the actual PLS section that has "available in" followed by language codes
            content_pattern = rf'{re.escape(section_name)}\s*\n(?:available in\s*\n)?(?:English|Español|Français|简体中文|繁體中文|한국어|日本語|Bahasa Malaysia|Polski|Română|Русский|ภาษาไทย|فارسی)'
            match = re.search(content_pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.start()

        # For Methods, Results, Background, and Objectives, look for the actual content sections, not navigation
        if section_name.lower() in ['methods', 'results', 'background', 'objectives']:
            # Look for the actual content sections that have subsections
            content_patterns = [
                # Methods content patterns
                rf'{re.escape(section_name)}\s*\n(?:Criteria for considering studies|Types of studies|Search methods|Data collection)',
                # Results content patterns  
                rf'{re.escape(section_name)}\s*\n(?:Description of studies|Results of the search|Included studies|Excluded studies)',
                # Background content patterns - distinguish from Abstract subsections
                rf'{re.escape(section_name)}\s*\n(?:Description of the condition|The extrauterine|Why it is important)',
                # Objectives content patterns - the standalone section comes after Background
                rf'{re.escape(section_name)}\s*\n(?:To determine|To assess|To evaluate|To compare|To review|To investigate).*?\n(?=Methods)',
                # General pattern for content sections
                rf'{re.escape(section_name)}\s*\n[A-Z][a-z].*?(?:\n[A-Z][a-z]|\n[A-Z][a-z][a-z])'
            ]
            
            for pattern in content_patterns:
                match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                if match:
                    return match.start()

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.start()

        return None
    
    def _extract_until_next_section(self, content: str, start_pos: int, section_name: str) -> str:
        """
        Extract content until the next major section.

        Args:
            content: Full content
            start_pos: Start position of current section
            section_name: Name of current section

        Returns:
            Extracted section content
        """
        # Define all possible next sections in order of appearance
        all_sections = [
            'Abstract', 'PICOs', 'Plain language summary', 'Authors\' conclusions',
            'Summary of findings', 'Background', 'Objectives', 'Methods', 'Results', 'Discussion'
        ]
        
        # Remove current section from the list
        next_sections = [s for s in all_sections if s.lower() != section_name.lower()]
        
        end_pos = len(content)
        
        # For Abstract section, we need to be more careful about boundaries
        if section_name.lower() == 'abstract':
            # Look for the next major section that's not Abstract
            for next_section in next_sections:
                patterns = [
                    rf'\n{re.escape(next_section)}\s*\n',
                    rf'\n{re.escape(next_section)}\s*\n(?:available in\s*\n)?',
                    rf'\n{re.escape(next_section)}\s*\n[A-Z]',
                    rf'\n{re.escape(next_section)}[:\s]*[A-Z]'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if match:
                        potential_end = start_pos + match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        # Special handling for Plain Language Summary - has subsections that might be confused with next sections
        elif section_name.lower() == 'plain language summary':
            # Look for the actual major sections that come after PLS (not PLS subsections)
            # Major sections have specific patterns that distinguish them from PLS subsections
            patterns = [
                # Summary of findings - look for table content
                rf'\nSummary of findings\s*\n(?:Open in|Summary of findings\s+\d+)',
                # Authors' conclusions - look for it appearing as a major section with specific content
                rf'\nAuthors\' conclusions\s*\n(?:Implications for|At present)',
                # Background - look for it with specific subsections that don't exist in PLS
                rf'\nBackground\s*\n(?:Description of the condition|The extrauterine|Why it is important)',
                # Objectives - look for it followed by Methods
                rf'\nObjectives\s*\n(?:To determine).*?\n(?=Methods)',
                # Methods - look for standard Methods subsections
                rf'\nMethods\s*\n(?:Criteria for considering|Types of studies|Search methods)',
                # Results - look for standard Results subsections  
                rf'\nResults\s*\n(?:Description of studies|Results of the search|Included studies)',
                # Discussion - look for it as the last major section
                rf'\nDiscussion\s*\n[A-Z][a-z].*\n(?:Summary of main results|Overall completeness|Quality of the evidence|Potential biases)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE | re.DOTALL)
                if match:
                    potential_end = start_pos + match.start()
                    if potential_end < end_pos:
                        end_pos = potential_end
                    break
        
        # Special handling for Methods section - often has subsections that might be confused with next sections
        elif section_name.lower() == 'methods':
            # Look for specific Methods subsections that might be confused with next major sections
            methods_subsections = [
                'criteria for considering studies for this review',
                'search methods for identification of studies',
                'data collection and analysis',
                'selection of studies',
                'data extraction and management',
                'assessment of risk of bias in included studies',
                'measures of treatment effect',
                'unit of analysis issues',
                'dealing with missing data',
                'assessment of heterogeneity',
                'assessment of reporting biases',
                'data synthesis',
                'subgroup analysis and investigation of heterogeneity',
                'sensitivity analysis'
            ]
            
            # Only look for major sections that are NOT Methods subsections
            major_sections_only = ['Results', 'Discussion', 'Authors\' conclusions', 'Summary of findings']
            for next_section in major_sections_only:
                patterns = [
                    rf'\n{re.escape(next_section)}\s*\n',
                    rf'\n{re.escape(next_section)}\s*\n(?:available in\s*\n)?',
                    rf'\n{re.escape(next_section)}\s*\n[A-Z]',
                    rf'\n{re.escape(next_section)}[:\s]*[A-Z]'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if match:
                        potential_end = start_pos + match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        # Special handling for Results section - often has subsections that might be confused with next sections
        elif section_name.lower() == 'results':
            # Look for specific Results subsections that might be confused with next major sections
            results_subsections = [
                'description of studies',
                'results of the search',
                'included studies',
                'excluded studies',
                'risk of bias in included studies',
                'methodology characteristics',
                'patient characteristics',
                'interventions',
                'outcomes'
            ]
            
            # Only look for major sections that are NOT Results subsections
            major_sections_only = ['Discussion', 'Authors\' conclusions', 'Summary of findings']
            for next_section in major_sections_only:
                patterns = [
                    rf'\n{re.escape(next_section)}\s*\n',
                    rf'\n{re.escape(next_section)}\s*\n(?:available in\s*\n)?',
                    rf'\n{re.escape(next_section)}\s*\n[A-Z]',
                    rf'\n{re.escape(next_section)}[:\s]*[A-Z]'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if match:
                        potential_end = start_pos + match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        # Special handling for Objectives section - it comes before Methods and should stop at Methods section start
        elif section_name.lower() == 'objectives':
            # Look for the Methods section start, or Background if Objectives is mispositioned
            for next_section in ['Background', 'Methods', 'Results', 'Discussion']:
                patterns = [
                    rf'\n{re.escape(next_section)}\s*\n',
                    rf'\n{re.escape(next_section)}\s*\n[A-Z]',
                    rf'\n{re.escape(next_section)}[:\s]*[A-Z]'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if match:
                        potential_end = start_pos + match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        # Special handling for Discussion section - it's often the last major section
        elif section_name.lower() == 'discussion':
            # Look for common end markers that indicate the end of the Discussion
            end_markers = [
                r'Figures and tables',
                r'References',
                r'Supplementary materials',
                r'Search strategies',
                r'Characteristics of studies',
                r'Analyses',
                r'Download data',
                r'Related',
                r'Cochrane Clinical Answers',
                r'Editorials',
                r'Audio summaries',
                r'Special Collections',
                r'About this review',
                r'Information',
                r'Authors',
                r'Version history',
                r'Keywords',
                r'Related content',
                r'Translation notes',
                r'Request permissions',
                r'Request data reuse'
            ]
            
            for marker in end_markers:
                pattern = rf'{re.escape(marker)}'
                match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE)
                if match:
                    potential_end = start_pos + match.start()
                    if potential_end < end_pos:
                        end_pos = potential_end
                    break
            
            # If no end markers found, Discussion might be the last section
            # Check if we're near the end of the content
            if end_pos > len(content) * 0.9:  # If we're in the last 10% of content
                end_pos = len(content)  # Take everything to the end
        
        else:
            # For other sections, use improved logic with better pattern matching
            for next_section in next_sections:
                patterns = [
                    rf'^{re.escape(next_section)}\s*\n',
                    rf'{re.escape(next_section)}\s*\n(?:available in\s*\n)?',
                    rf'{re.escape(next_section)}\s*\n[A-Z]',
                    rf'{re.escape(next_section)}[:\s]*[A-Z]',
                    rf'\n{re.escape(next_section)}\s*\n',
                    rf'\n{re.escape(next_section)}\s*\n(?:available in\s*\n)?',
                    # Additional patterns for better coverage
                    rf'\n\s*{re.escape(next_section)}\s*\n',
                    rf'\n\s*{re.escape(next_section)}\s*$',
                    rf'^{re.escape(next_section)}\s*$'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if match:
                        potential_end = start_pos + match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        return content[start_pos:end_pos].strip()
    
    def _extract_subsection_content(self, section_text: str, subsection_name: str, 
                                  next_subsection_names: list = None) -> Optional[str]:
        """
        Extract content for a specific subsection.
        
        Args:
            section_text: Text of the parent section
            subsection_name: Name of the subsection to extract
            next_subsection_names: List of possible next subsection names
            
        Returns:
            Subsection content if found, None otherwise
        """
        # Convert underscore-separated names to space-separated names for matching
        # e.g., 'search_methods' -> 'search methods'
        normalized_name = subsection_name.replace('_', ' ')
        
        # Create pattern for the subsection
        patterns = [
            rf'^{re.escape(normalized_name)}\s*\n',
            rf'{re.escape(normalized_name)}\s*\n(?:available in\s*\n)?',
            rf'{re.escape(normalized_name)}\s*\n[A-Z]',
            rf'{re.escape(normalized_name)}[:\s]*[A-Z]'
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
                # Normalize next subsection name too
                normalized_next = next_subsection.replace('_', ' ')
                next_patterns = [
                    rf'^{re.escape(normalized_next)}\s*\n',
                    rf'{re.escape(normalized_next)}\s*\n[A-Z]',
                    rf'{re.escape(normalized_next)}[:\s]*[A-Z]'
                ]
                
                for next_pattern in next_patterns:
                    next_match = re.search(next_pattern, section_text[start_pos:], re.MULTILINE | re.IGNORECASE)
                    if next_match:
                        potential_end = start_pos + next_match.start()
                        if potential_end < end_pos:
                            end_pos = potential_end
                        break
        
        return section_text[start_pos:end_pos].strip()
