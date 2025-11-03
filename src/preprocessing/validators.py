"""
File validation component for Cochrane RAG system.

This module handles validation of raw Cochrane JSON files,
following single responsibility principle.
"""

import json
import re
from typing import List
from src.core.data_models import RawCochraneData, ValidationResult, QualityGrade


class FileValidator:
    """Validates raw Cochrane JSON files."""
    
    MIN_ABSTRACT_LENGTH = 100
    DOI_PATTERN = re.compile(r'^10\.\d{4,}/[^\s]+$')
    
    def validate(self, raw_data: RawCochraneData) -> ValidationResult:
        """
        Validate raw Cochrane data.
        
        Args:
            raw_data: Raw data to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Validate required fields
        errors.extend(self._validate_required_fields(raw_data))
        
        # Validate field formats
        errors.extend(self._validate_field_formats(raw_data))
        
        # Validate content quality
        warnings.extend(self._validate_content_quality(raw_data))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_required_fields(self, raw_data: RawCochraneData) -> List[str]:
        """Validate that all required fields are present and non-empty."""
        errors = []
        
        if not raw_data.title or not raw_data.title.strip():
            errors.append("Title is required and cannot be empty")
        
        # Abstract or full_content must be present (not both required)
        if (not raw_data.abstract or not raw_data.abstract.strip()) and \
           (not raw_data.full_content or not raw_data.full_content.strip()):
            errors.append("Either abstract or full_content is required")
        
        if not raw_data.doi or not raw_data.doi.strip():
            errors.append("DOI is required and cannot be empty")
        
        if not raw_data.authors or len(raw_data.authors) == 0:
            errors.append("Authors list is required and cannot be empty")
        
        if not raw_data.topic_name or not raw_data.topic_name.strip():
            errors.append("Topic name is required and cannot be empty")
        
        if not raw_data.quality:
            errors.append("Quality information is required")
        
        return errors
    
    def _validate_field_formats(self, raw_data: RawCochraneData) -> List[str]:
        """Validate field formats and data types."""
        errors = []
        
        # Validate DOI format
        if raw_data.doi and not self.DOI_PATTERN.match(raw_data.doi):
            errors.append(f"Invalid DOI format: {raw_data.doi}")
        
        # Validate quality grade
        if raw_data.quality:
            grade = raw_data.quality.get('grade')
            if grade and grade not in [g.value for g in QualityGrade]:
                errors.append(f"Invalid quality grade: {grade}")
        
        # Validate authors list
        if raw_data.authors:
            for i, author in enumerate(raw_data.authors):
                if not isinstance(author, str) or not author.strip():
                    errors.append(f"Invalid author at index {i}: {author}")
        
        return errors
    
    def _validate_content_quality(self, raw_data: RawCochraneData) -> List[str]:
        """Validate content quality and generate warnings."""
        warnings = []
        
        # Check abstract length
        if raw_data.abstract and len(raw_data.abstract.strip()) < self.MIN_ABSTRACT_LENGTH:
            warnings.append(f"Abstract is short ({len(raw_data.abstract)} chars), minimum recommended: {self.MIN_ABSTRACT_LENGTH}")
        
        # Check title length
        if raw_data.title and len(raw_data.title.strip()) < 10:
            warnings.append("Title appears to be very short")
        
        # Check for missing full content
        if not raw_data.full_content or not raw_data.full_content.strip():
            warnings.append("Full content is missing or empty")
        
        return warnings


class JsonValidator:
    """Validates JSON structure and format."""
    
    def validate_json_structure(self, json_data: dict) -> ValidationResult:
        """
        Validate JSON structure for required fields.
        
        Args:
            json_data: JSON data to validate
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        
        required_fields = [
            'title', 'abstract', 'doi', 'authors', 
            'topic_name', 'quality', 'url'
        ]
        
        for field in required_fields:
            if field not in json_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate quality object structure
        if 'quality' in json_data:
            quality = json_data['quality']
            if not isinstance(quality, dict):
                errors.append("Quality field must be an object")
            elif 'grade' not in quality:
                errors.append("Quality object missing 'grade' field")
        
        # Validate authors is a list
        if 'authors' in json_data:
            if not isinstance(json_data['authors'], list):
                errors.append("Authors field must be a list")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors
        )
