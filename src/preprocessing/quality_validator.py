"""
Quality control and validation component for Cochrane RAG system.

This module handles final quality validation of processed documents,
following single responsibility principle.
"""

from typing import List, Optional
from src.core.data_models import ProcessedDocument, ProcessingResult, ValidationResult


class QualityValidator:
    """Validates quality of processed documents."""
    
    MIN_CONTENT_LENGTH = 500
    MIN_SECTIONS = 2
    MIN_PICO_ELEMENTS = 1
    
    def validate_processed_document(self, document: ProcessedDocument) -> ValidationResult:
        """
        Validate the quality of a processed document.
        
        Args:
            document: Processed document to validate
            
        Returns:
            ValidationResult with validation status and any issues
        """
        errors = []
        warnings = []
        
        # Validate content completeness
        errors.extend(self._validate_content_completeness(document))
        
        # Validate PICO elements
        warnings.extend(self._validate_pico_elements(document))
        
        
        # Validate medical entities
        warnings.extend(self._validate_medical_entities(document))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_content_completeness(self, document: ProcessedDocument) -> List[str]:
        """Validate that content is complete and sufficient."""
        errors = []
        
        # Check content length
        if document.metadata.content_length < self.MIN_CONTENT_LENGTH:
            errors.append(f"Content too short: {document.metadata.content_length} chars, minimum: {self.MIN_CONTENT_LENGTH}")
        
        # Check section count
        if document.metadata.section_count < self.MIN_SECTIONS:
            errors.append(f"Insufficient sections: {document.metadata.section_count}, minimum: {self.MIN_SECTIONS}")
        
        # Check if at least one major section exists (more lenient than requiring specific sections)
        major_sections = ['abstract', 'background', 'objectives', 'methods', 'results', 'discussion']
        found_sections = [s for s in major_sections if s in document.sections.sections]
        
        if len(found_sections) == 0 and document.metadata.section_count >= self.MIN_SECTIONS:
            # We have sections but none of the expected major ones
            # This is a warning, not an error
            pass
        
        return errors
    
    def _validate_pico_elements(self, document: ProcessedDocument) -> List[str]:
        """Validate PICO elements extraction."""
        warnings = []
        
        pico = document.metadata.pico_elements
        
        # Check if we have sufficient PICO elements
        total_pico_elements = (
            len(pico.population) + len(pico.intervention) + 
            len(pico.comparison) + len(pico.outcome)
        )
        
        if total_pico_elements < self.MIN_PICO_ELEMENTS:
            warnings.append(f"Limited PICO elements extracted: {total_pico_elements}")
        
        # Check for empty PICO categories
        if not pico.population:
            warnings.append("No population elements extracted")
        
        if not pico.intervention:
            warnings.append("No intervention elements extracted")
        
        if not pico.outcome:
            warnings.append("No outcome elements extracted")
        
        return warnings
    
    
    def _validate_medical_entities(self, document: ProcessedDocument) -> List[str]:
        """Validate medical entity extraction."""
        warnings = []
        
        entities = document.metadata.medical_entities
        
        # Check for medical entities
        total_entities = (
            len(entities.conditions) + len(entities.drugs) + 
            len(entities.procedures) + len(entities.outcomes)
        )
        
        if total_entities == 0:
            warnings.append("No medical entities extracted")
        
        # Check specific entity types
        if not entities.conditions:
            warnings.append("No medical conditions identified")
        
        if not entities.outcomes:
            warnings.append("No outcome measures identified")
        
        return warnings


class ProcessingResultValidator:
    """Validates processing results and generates quality reports."""
    
    def validate_processing_result(self, result: ProcessingResult) -> ValidationResult:
        """
        Validate a processing result.
        
        Args:
            result: Processing result to validate
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        if not result.success:
            errors.append("Processing failed")
            if result.errors:
                errors.extend(result.errors)
        
        if result.processing_time > 30.0:  # More than 30 seconds
            warnings.append(f"Processing took longer than expected: {result.processing_time:.2f}s")
        
        if result.document:
            # Validate the document quality
            doc_validator = QualityValidator()
            doc_validation = doc_validator.validate_processed_document(result.document)
            errors.extend(doc_validation.errors)
            warnings.extend(doc_validation.warnings)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def generate_quality_report(self, results: List[ProcessingResult]) -> dict:
        """
        Generate a quality report for multiple processing results.
        
        Args:
            results: List of processing results
            
        Returns:
            Dictionary with quality metrics and issues
        """
        total_results = len(results)
        successful_results = sum(1 for r in results if r.success)
        failed_results = total_results - successful_results
        
        # Collect all errors and warnings
        all_errors = []
        all_warnings = []
        
        for result in results:
            if result.errors:
                all_errors.extend(result.errors)
            
            validation = self.validate_processing_result(result)
            all_warnings.extend(validation.warnings)
        
        # Count error types
        error_counts = {}
        for error in all_errors:
            error_type = error.split(':')[0] if ':' in error else error
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Count warning types
        warning_counts = {}
        for warning in all_warnings:
            warning_type = warning.split(':')[0] if ':' in warning else warning
            warning_counts[warning_type] = warning_counts.get(warning_type, 0) + 1
        
        return {
            'total_processed': total_results,
            'successful': successful_results,
            'failed': failed_results,
            'success_rate': successful_results / total_results if total_results > 0 else 0,
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'error_types': error_counts,
            'warning_types': warning_counts,
            'common_errors': sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'common_warnings': sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
