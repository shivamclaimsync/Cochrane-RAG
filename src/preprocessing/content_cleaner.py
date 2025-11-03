"""
Content cleaning component for Cochrane RAG system.

This module handles cleaning and standardization of raw content,
following single responsibility principle.
"""

import re
from typing import List
from src.core.data_models import RawCochraneData, CleanedContent, QualityGrade


class ContentCleaner:
    """Cleans and standardizes raw Cochrane content."""
    
    # Navigation and TOC patterns to remove
    NAVIGATION_PATTERNS = [
        r'Download PDF',
        r'Comment',
        r'Share',
        r'Sign up to email alerts',
        r'Citations',
        r'Full text views:.*?',
        r'Contents\s*\n',  # Only remove TOC entries, not actual sections
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
        r'Keywords \(MeSH, PICOs\)',
        r'Related content',
        r'Translation notes',
        r'Request permissions',
        r'Request data reuse'
    ]
    
    def clean_content(self, raw_data: RawCochraneData) -> CleanedContent:
        """
        Clean and standardize raw content.
        
        Args:
            raw_data: Raw data to clean
            
        Returns:
            CleanedContent with standardized content
        """
        cleaned_title = self._clean_title(raw_data.title)
        cleaned_abstract = self._clean_abstract(raw_data.abstract)
        cleaned_full_content = self._clean_full_content(raw_data.full_content or "")
        cleaned_authors = self._clean_authors(raw_data.authors)
        quality_grade = self._extract_quality_grade(raw_data.quality)
        
        return CleanedContent(
            title=cleaned_title,
            abstract=cleaned_abstract,
            full_content=cleaned_full_content,
            authors=cleaned_authors,
            doi=raw_data.doi.strip(),
            topic_name=raw_data.topic_name.strip(),
            quality_grade=quality_grade,
            url=raw_data.url if raw_data.url else ''
        )
    
    def _clean_title(self, title: str) -> str:
        """Clean and standardize title."""
        if not title:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', title.strip())
        
        # Remove any navigation elements that might have leaked in
        for pattern in self.NAVIGATION_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _clean_abstract(self, abstract: str) -> str:
        """Clean and standardize abstract."""
        if not abstract:
            return ""
        
        # For abstract, only remove basic navigation elements, not section headers
        # Section headers are needed for extraction
        cleaned = abstract
        
        # Remove only basic navigation elements that don't contain section content
        basic_nav_patterns = [
            r'Download PDF',
            r'Comment',
            r'Share',
            r'Sign up to email alerts',
            r'Citations',
            r'Full text views:.*?',
        ]
        
        for pattern in basic_nav_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Normalize whitespace but preserve line breaks for section structure
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Only normalize spaces and tabs
        cleaned = re.sub(r'\n+', '\n', cleaned)    # Normalize multiple newlines
        
        return cleaned.strip()
    
    def _clean_full_content(self, content: str) -> str:
        """Clean and standardize full content."""
        if not content:
            return ""
        
        # Remove navigation elements
        cleaned = self._remove_navigation_elements(content)
        
        # Find actual content start (skip TOC/navigation)
        content_start = self._find_content_start(cleaned)
        if content_start > 0:
            cleaned = cleaned[content_start:]
        
        # Normalize whitespace but preserve line breaks for section structure
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Only normalize spaces and tabs
        cleaned = re.sub(r'\n+', '\n', cleaned)    # Normalize multiple newlines
        
        return cleaned.strip()
    
    def _clean_authors(self, authors: List[str]) -> List[str]:
        """Clean and standardize author list."""
        if not authors:
            return []
        
        cleaned_authors = []
        for author in authors:
            if isinstance(author, str) and author.strip():
                # Remove extra whitespace and normalize
                cleaned_author = re.sub(r'\s+', ' ', author.strip())
                cleaned_authors.append(cleaned_author)
        
        return cleaned_authors
    
    def _extract_quality_grade(self, quality: dict) -> QualityGrade:
        """Extract quality grade from quality dictionary."""
        if not quality or 'grade' not in quality:
            return QualityGrade.C
        
        grade_value = quality['grade']
        try:
            return QualityGrade(grade_value)
        except ValueError:
            return QualityGrade.C
    
    def _remove_navigation_elements(self, text: str) -> str:
        """Remove navigation and TOC elements from text."""
        cleaned = text
        
        for pattern in self.NAVIGATION_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        return cleaned
    
    def _find_content_start(self, text: str) -> int:
        """Find the start of actual content by looking for major sections."""
        # Look for Abstract with actual content (not just TOC entry)
        abstract_pattern = re.compile(r'Abstract\navailable in\n', re.MULTILINE | re.IGNORECASE)
        match = abstract_pattern.search(text)
        if match:
            return match.start()
        
        # Look for other sections with actual content
        content_patterns = [
            r'Background\navailable in\n',
            r'PICOs\nPopulation\s*\(',
            r'Plain language summary\navailable in\n',
            r'Authors\' conclusions\navailable in\n'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.start()
        
        return 0
