"""
Preprocessing module for data ingestion and preparation.

This module handles the complete data preprocessing pipeline including:
- File validation and cleaning
- Content extraction and structuring
- PICO element extraction
- Metadata enrichment
- Quality validation
- Enhanced batch processing with progress tracking
- Configurable pipeline management
"""

# Core pipeline components
from .pipeline import CochraneProcessingPipeline
from .validators import FileValidator
from .content_cleaner import ContentCleaner
from .extractors.section_extractor import SectionExtractor
from .pico_extractor import PicoExtractor
from .metadata_enricher import MetadataEnricher
from .quality_validator import QualityValidator

# Enhanced pipeline components
try:
    from .config import (
        PreprocessingConfig, 
        get_default_config, 
        get_fast_config, 
        get_quality_config, 
        get_debug_config
    )
except ImportError:
    PreprocessingConfig = None
    get_default_config = None
    get_fast_config = None
    get_quality_config = None
    get_debug_config = None

try:
    from .batch_processor import BatchProcessor
    from .progress_tracker import ProgressTracker, ProcessingStats, FileProcessingResult
except ImportError:
    BatchProcessor = None
    ProgressTracker = None
    ProcessingStats = None
    FileProcessingResult = None

__all__ = [
    # Core components
    'CochraneProcessingPipeline',
    'FileValidator',
    'ContentCleaner',
    'SectionExtractor',
    'PicoExtractor',
    'MetadataEnricher',
    'QualityValidator',
    
    # Enhanced components
    'PreprocessingConfig',
    'BatchProcessor',
    'ProgressTracker',
    'ProcessingStats',
    'FileProcessingResult',
    
    # Configuration helpers
    'get_default_config',
    'get_fast_config',
    'get_quality_config',
    'get_debug_config'
]
