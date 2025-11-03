"""
Main processing pipeline orchestrator for Cochrane RAG system.

This module orchestrates the entire preprocessing pipeline,
following clean code principles and single responsibility principle.
"""

import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.core.data_models import (
    RawCochraneData, ProcessedDocument, ProcessingResult, ProcessingStats
)
from .validators import FileValidator
from .content_cleaner import ContentCleaner
from .extractors.refactored_section_extractor import RefactoredSectionExtractor
from .pico_extractor import PicoExtractor
from .metadata_enricher import MetadataEnricher
from .quality_validator import QualityValidator


class CochraneProcessingPipeline:
    """Main orchestrator for the Cochrane data processing pipeline."""
    
    def __init__(self):
        """Initialize the processing pipeline with all components."""
        self.file_validator = FileValidator()
        self.content_cleaner = ContentCleaner()
        self.section_extractor = RefactoredSectionExtractor()
        self.pico_extractor = PicoExtractor()
        self.metadata_enricher = MetadataEnricher()
        self.quality_validator = QualityValidator()

        self.stats = ProcessingStats()
    
    def process_file(self, file_path: Path) -> ProcessingResult:
        """
        Process a single Cochrane JSON file.
        
        Args:
            file_path: Path to the JSON file to process
            
        Returns:
            ProcessingResult with processing status and document
        """
        start_time = time.time()
        
        try:
            # Load and validate JSON
            raw_data = self._load_json_file(file_path)
            if not raw_data:
                return ProcessingResult(
                    success=False,
                    errors=["Failed to load JSON file"],
                    processing_time=time.time() - start_time
                )
            
            # Convert to RawCochraneData
            cochrane_data = self._convert_to_raw_data(raw_data, file_path.name)
            
            # Validate file structure
            file_validation = self.file_validator.validate(cochrane_data)
            if not file_validation.is_valid:
                return ProcessingResult(
                    success=False,
                    errors=file_validation.errors,
                    processing_time=time.time() - start_time
                )
            
            
            # Process the document through the pipeline
            processed_document = self._process_document(cochrane_data, file_path.name)
            
            # Validate final quality
            quality_validation = self.quality_validator.validate_processed_document(processed_document)
            if not quality_validation.is_valid:
                return ProcessingResult(
                    success=False,
                    errors=quality_validation.errors,
                    processing_time=time.time() - start_time
                )
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                document=processed_document,
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                errors=[f"Processing error: {str(e)}"],
                processing_time=time.time() - start_time
            )
    
    def process_directory(self, input_dir: Path, output_dir: Path, log_dir: Path, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Process all JSON files in a directory with log tracking.
        
        Args:
            input_dir: Directory containing JSON files
            output_dir: Directory to save processed files
            log_dir: Directory to store processing logs
            limit: Optional limit on number of files to process
            
        Returns:
            Dictionary with processing statistics and results
        """
        # Create output and log directories
        output_dir.mkdir(exist_ok=True, parents=True)
        log_dir.mkdir(exist_ok=True, parents=True)
        
        # Load existing processing log
        processed_files_log = self._load_processed_files(log_dir)
        log_file = self._get_log_file_path(log_dir)
        
        # Find JSON files
        json_files = list(input_dir.glob('*.json'))
        if limit:
            json_files = json_files[:limit]
        
        results = []
        skipped_count = 0
        
        for i, json_file in enumerate(json_files, 1):
            filename = json_file.name
            
            # Check if file is already processed
            if self._is_file_processed(processed_files_log, filename):
                print(f"Skipping [{i}/{len(json_files)}]: {filename} (already processed)")
                skipped_count += 1
                continue
            
            print(f"Processing [{i}/{len(json_files)}]: {filename}")
            
            result = self.process_file(json_file)
            results.append(result)
            
            # Determine status and timestamp
            status = "success" if result.success else "failed"
            timestamp = datetime.now().isoformat()
            
            # Save entry to log
            self._save_processed_file_entry(log_file, filename, status, timestamp)
            
            # Update processed files log in memory
            processed_files_log[filename] = {
                'filename': filename,
                'timestamp': timestamp,
                'status': status
            }
            
            # Update statistics
            self._update_stats(result)
            
            # Save successful results
            if result.success and result.document:
                self._save_processed_document(result.document, output_dir, json_file.stem)
        
        # Generate final report
        report = self._generate_processing_report(results, skipped_count)
        
        return report
    
    def _load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON file and return parsed data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def _get_log_file_path(self, log_dir: Path) -> Path:
        """Returns path to processing log JSON file."""
        return log_dir / "processing_log.json"
    
    def _load_processed_files(self, log_dir: Path) -> Dict[str, Dict]:
        """Loads existing log file and returns dictionary of processed files keyed by filename."""
        log_file = self._get_log_file_path(log_dir)
        
        if not log_file.exists():
            return {}
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                return log_data.get('processed_files', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading log file {log_file}: {e}")
            return {}
    
    def _save_processed_file_entry(self, log_file: Path, filename: str, status: str, timestamp: str) -> None:
        """Adds/updates entry in log file."""
        try:
            # Load existing log data
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {'processed_files': {}}
            
            # Update entry
            log_data.setdefault('processed_files', {})[filename] = {
                'filename': filename,
                'timestamp': timestamp,
                'status': status
            }
            
            # Save updated log
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error saving log entry for {filename}: {e}")
    
    def _is_file_processed(self, log_data: Dict[str, Dict], filename: str) -> bool:
        """Checks if file is already in log."""
        return filename in log_data
    
    def _convert_to_raw_data(self, json_data: Dict[str, Any], filename: str) -> RawCochraneData:
        """Convert JSON data to RawCochraneData object."""
        return RawCochraneData(
            url=json_data.get('url', ''),
            number=json_data.get('number', 0),
            timestamp=json_data.get('timestamp', 0.0),
            title=json_data.get('title', ''),
            doi=json_data.get('doi', ''),
            abstract=json_data.get('abstract', ''),
            authors=json_data.get('authors', []),
            topic_name=json_data.get('topic_name', ''),
            topic_page=json_data.get('topic_page', 0),
            quality=json_data.get('quality', {}),
            full_content=json_data.get('full_content', '')
        )
    
    def _process_document(self, raw_data: RawCochraneData, filename: str) -> ProcessedDocument:
        """Process document through the entire pipeline."""
        # Step 1: Clean content
        cleaned_content = self.content_cleaner.clean_content(raw_data)
        
        # Step 2: Extract sections
        sections = self.section_extractor.extract_sections(cleaned_content)
        
        # Step 3: Extract PICO elements
        pico_elements = self.pico_extractor.extract_pico_elements(sections)
        
        # Step 4: Enrich metadata
        enriched_metadata = self.metadata_enricher.enrich_metadata(
            cleaned_content, sections, pico_elements, filename
        )
        
        # Create ProcessedDocument with additional fields
        processed_doc = ProcessedDocument(
            metadata=enriched_metadata,
            sections=sections
        )
        
        
        return processed_doc
    
    def _save_processed_document(self, document: ProcessedDocument, output_dir: Path, filename: str):
        """Save processed document to JSON file."""
        output_file = output_dir / f"processed_{filename}.json"
        
        # Convert document to dictionary for JSON serialization
        doc_dict = {
            'metadata': {
                'source_file': document.metadata.source_file,
                'title': document.metadata.title,
                'doi': document.metadata.doi,
                'authors': document.metadata.authors,
                'url': document.metadata.url,
                'topic_name': document.metadata.topic_name,
                'quality_grade': document.metadata.quality_grade.value,
                'extraction_date': document.metadata.extraction_date,
                'content_length': document.metadata.content_length,
                'pico_elements': {
                    'population': document.metadata.pico_elements.population,
                    'intervention': document.metadata.pico_elements.intervention,
                    'comparison': document.metadata.pico_elements.comparison,
                    'outcome': document.metadata.pico_elements.outcome
                },
                'medical_entities': {
                    'conditions': document.metadata.medical_entities.conditions,
                    'drugs': document.metadata.medical_entities.drugs,
                    'procedures': document.metadata.medical_entities.procedures,
                    'outcomes': document.metadata.medical_entities.outcomes
                },
                'sections_extracted': document.metadata.sections_extracted,
                'section_count': document.metadata.section_count,
                'subsection_count': document.metadata.subsection_count
            },
            'sections': {
                name: {
                    'name': section.name,
                    'content': section.content,
                    'subsections': section.subsections
                }
                for name, section in document.sections.sections.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_dict, f, indent=2, ensure_ascii=False)
    
    def _update_stats(self, result: ProcessingResult):
        """Update processing statistics."""
        self.stats.total_processed += 1
        
        if result.success:
            self.stats.successful += 1
            if result.document:
                self.stats.total_sections += result.document.metadata.section_count
                self.stats.total_subsections += result.document.metadata.subsection_count
        else:
            self.stats.failed += 1
    
    def _generate_processing_report(self, results: List[ProcessingResult], skipped_count: int = 0) -> Dict[str, Any]:
        """Generate comprehensive processing report."""
        total_processed = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total_processed - successful
        
        # Calculate average processing time
        avg_processing_time = sum(r.processing_time for r in results) / total_processed if total_processed > 0 else 0
        
        # Collect errors
        all_errors = []
        for result in results:
            all_errors.extend(result.errors)
        
        return {
            'processing_summary': {
                'total_processed': total_processed,
                'successful': successful,
                'failed': failed,
                'skipped': skipped_count,
                'success_rate': successful / total_processed if total_processed > 0 else 0,
                'average_processing_time': avg_processing_time
            },
            'statistics': {
                'total_sections': self.stats.total_sections,
                'total_subsections': self.stats.total_subsections,
                'average_sections_per_document': self.stats.total_sections / successful if successful > 0 else 0,
                'average_subsections_per_document': self.stats.total_subsections / successful if successful > 0 else 0
            },
            'quality_metrics': {
                'total_errors': len(all_errors),
                'error_rate': len(all_errors) / total_processed if total_processed > 0 else 0
            },
            'common_issues': {
                'errors': self._count_issue_types(all_errors)
            }
        }
    
    def _count_issue_types(self, issues: List[str]) -> Dict[str, int]:
        """Count occurrences of different issue types."""
        issue_counts = {}
        for issue in issues:
            issue_type = issue.split(':')[0] if ':' in issue else issue
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        return dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))
