# 🚀 Enhanced Preprocessing Pipeline

A comprehensive, configurable preprocessing pipeline for Cochrane data with advanced features including batch processing, progress tracking, and flexible configuration management.

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Command Line Interface](#command-line-interface)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 🎯 **Core Capabilities**
- **Unified Interface**: Single entry point for all processing operations
- **Batch Processing**: Process multiple files with parallel execution
- **Progress Tracking**: Real-time monitoring with detailed statistics
- **Flexible Configuration**: Easy customization without code changes
- **Error Handling**: Comprehensive error management and reporting
- **Multiple Output Formats**: JSON, YAML, and more

### 🔧 **Advanced Features**
- **Parallel Processing**: Multi-threaded processing for improved performance
- **Memory Management**: Batch processing to handle large datasets
- **Real-time Monitoring**: Callbacks and progress tracking
- **Configuration Presets**: Pre-configured settings for different use cases
- **Validation**: Comprehensive input and output validation
- **Logging**: Detailed processing logs and statistics

## 🚀 Quick Start

### Basic Usage

```python
from src.preprocessing import EnhancedCochranePipeline

# Initialize with default configuration
pipeline = EnhancedCochranePipeline()

# Process a single file
result = pipeline.process_single_file("input.json", "output.json")

# Process a directory
result = pipeline.process_directory("raw/json/", "processed/")
```

### With Custom Configuration

```python
from src.preprocessing import EnhancedCochranePipeline, PreprocessingConfig

# Create custom configuration
config = PreprocessingConfig(
    max_workers=8,
    batch_size=50,
    strict_validation=True,
    extract_subsections=True
)

# Initialize pipeline
pipeline = EnhancedCochranePipeline(config)

# Process data
result = pipeline.process_raw_data("raw/json/", "processed/")
```

## ⚙️ Configuration

### Configuration Presets

The pipeline comes with several pre-configured presets:

```python
from src.preprocessing import get_default_config, get_fast_config, get_quality_config, get_debug_config

# Default configuration
config = get_default_config()

# Fast processing (optimized for speed)
config = get_fast_config()

# Quality processing (optimized for accuracy)
config = get_quality_config()

# Debug configuration (for development)
config = get_debug_config()
```

### Custom Configuration

```python
from src.preprocessing import PreprocessingConfig

config = PreprocessingConfig(
    # Input/Output settings
    input_dir=Path("raw/json"),
    output_dir=Path("processed"),
    
    # Processing settings
    max_workers=4,
    batch_size=100,
    enable_parallel=True,
    
    # Quality settings
    min_sections=2,
    min_content_length=100,
    strict_validation=False,
    
    # Output settings
    save_individual=True,
    save_summary=True,
    include_full_content=True,
    include_url=True,
    
    # Progress tracking
    show_progress=True,
    save_processing_log=True
)
```

### Configuration Files

Save and load configurations:

```python
# Save configuration
config.to_json("my_config.json")
config.to_yaml("my_config.yaml")

# Load configuration
config = PreprocessingConfig.from_json("my_config.json")
config = PreprocessingConfig.from_yaml("my_config.yaml")
```

## 📚 Usage Examples

### Example 1: Single File Processing

```python
from src.preprocessing import EnhancedCochranePipeline

pipeline = EnhancedCochranePipeline()

# Process a single file
result = pipeline.process_single_file(
    "raw/json/sample.json", 
    "processed/sample_processed.json"
)

if result['success']:
    print(f"✅ Processed: {result['result'].sections_extracted} sections")
    print(f"⏱️  Time: {result['processing_time']:.2f}s")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 2: Batch Processing with Progress Tracking

```python
from src.preprocessing import EnhancedCochranePipeline, get_quality_config

# Set up progress callback
def progress_callback(result):
    status = "✅" if result.success else "❌"
    print(f"{status} {result.file_name}: {result.sections_extracted} sections")

# Initialize pipeline
config = get_quality_config()
pipeline = EnhancedCochranePipeline(config)

# Process with monitoring
result = pipeline.process_with_monitoring(
    "raw/json/", 
    "processed/", 
    progress_callback
)

print(f"🎯 Processed {result['processed_files']} files")
print(f"📈 Success rate: {result['stats']['success_rate']:.1f}%")
```

### Example 3: Custom Configuration

```python
from src.preprocessing import EnhancedCochranePipeline, PreprocessingConfig

# Create custom configuration
config = PreprocessingConfig(
    max_workers=6,
    batch_size=25,
    min_sections=3,
    strict_validation=True,
    extract_subsections=True,
    show_progress=True
)

# Initialize pipeline
pipeline = EnhancedCochranePipeline(config)

# Process data
result = pipeline.process_raw_data("raw/json/", "processed/")
```

### Example 4: Error Handling and Statistics

```python
from src.preprocessing import EnhancedCochranePipeline

pipeline = EnhancedCochranePipeline()

result = pipeline.process_directory("raw/json/", "processed/")

if result['success']:
    stats = result['stats']
    print(f"✅ Success: {stats['processed_files']} files")
    print(f"❌ Failed: {stats['failed_files']} files")
    print(f"📈 Success rate: {stats['success_rate']:.1f}%")
    print(f"⏱️  Total time: {stats['total_processing_time']:.2f}s")
    print(f"🚀 Throughput: {stats['throughput']:.2f} files/s")
    
    # Error breakdown
    if stats['error_types']:
        print("❌ Error breakdown:")
        for error_type, count in stats['error_types'].items():
            print(f"   {error_type}: {count} files")
else:
    print(f"❌ Processing failed: {result['error']}")
```

## 🔧 API Reference

### EnhancedCochranePipeline

Main pipeline class for processing Cochrane data.

#### Methods

- `process_raw_data(input_path, output_path=None, callback=None)`: Main entry point
- `process_single_file(input_path, output_path, callback=None)`: Process single file
- `process_directory(input_dir, output_dir, callback=None)`: Process directory
- `process_with_monitoring(input_path, output_path, callback)`: Process with monitoring
- `get_config()`: Get current configuration
- `update_config(**kwargs)`: Update configuration
- `validate_config()`: Validate configuration
- `get_processing_stats()`: Get processing statistics

### PreprocessingConfig

Configuration class for pipeline settings.

#### Key Parameters

- `max_workers`: Number of parallel workers
- `batch_size`: Batch size for processing
- `min_sections`: Minimum sections required
- `strict_validation`: Enable strict validation
- `extract_subsections`: Extract subsections
- `show_progress`: Show progress bar
- `save_processing_log`: Save processing log

### ProgressTracker

Progress tracking and statistics collection.

#### Methods

- `start_batch(total_files, description)`: Start tracking
- `update_progress(result)`: Update progress
- `finish_batch()`: Finish tracking
- `get_summary()`: Get processing summary

## 💻 Command Line Interface

The pipeline includes a command-line interface for easy usage:

### Basic Commands

```bash
# Process a single file
python -m src.preprocessing.cli process single input.json output.json

# Process a directory
python -m src.preprocessing.cli process batch raw/json/ processed/

# Process with quality settings
python -m src.preprocessing.cli process batch raw/json/ processed/ --preset quality

# Process with custom configuration
python -m src.preprocessing.cli process batch raw/json/ processed/ --config my_config.json
```

### Configuration Commands

```bash
# Generate configuration file
python -m src.preprocessing.cli config generate --preset quality --output config.json

# Validate configuration file
python -m src.preprocessing.cli config validate config.json
```

### Advanced Options

```bash
# Process with custom settings
python -m src.preprocessing.cli process batch raw/json/ processed/ \
    --workers 8 \
    --batch-size 50 \
    --min-sections 3 \
    --strict \
    --monitor
```

## 🔍 Advanced Usage

### Custom Progress Callbacks

```python
def detailed_callback(result):
    if result.success:
        print(f"✅ {result.file_name}")
        print(f"   Sections: {result.sections_extracted}")
        print(f"   Subsections: {result.subsections_extracted}")
        print(f"   Content: {result.content_length:,} chars")
        print(f"   Time: {result.processing_time:.2f}s")
    else:
        print(f"❌ {result.file_name}: {result.error_message}")

pipeline.process_with_monitoring("raw/json/", "processed/", detailed_callback)
```

### Memory-Efficient Processing

```python
# Use smaller batch sizes for large datasets
config = PreprocessingConfig(
    batch_size=10,  # Smaller batches
    max_workers=2   # Fewer workers to reduce memory usage
)

pipeline = EnhancedCochranePipeline(config)
result = pipeline.process_directory("large_dataset/", "processed/")
```

### Custom Error Handling

```python
def error_callback(result):
    if not result.success:
        # Log specific error types
        if result.error_type == 'validation_error':
            print(f"Validation failed for {result.file_name}: {result.error_message}")
        elif result.error_type == 'processing_error':
            print(f"Processing failed for {result.file_name}: {result.error_message}")

pipeline.process_with_monitoring("raw/json/", "processed/", error_callback)
```

## 🐛 Troubleshooting

### Common Issues

1. **Memory Issues**: Reduce `batch_size` and `max_workers`
2. **Validation Errors**: Check `min_sections` and `min_content_length` settings
3. **Slow Processing**: Increase `max_workers` or use `get_fast_config()`
4. **Missing Sections**: Use `get_quality_config()` for better extraction

### Debug Mode

```python
from src.preprocessing import get_debug_config

config = get_debug_config()
pipeline = EnhancedCochranePipeline(config)
```

### Logging

Enable detailed logging:

```python
config = PreprocessingConfig(
    save_processing_log=True,
    log_level="DEBUG"
)

pipeline = EnhancedCochranePipeline(config)
```

## 📊 Performance Tips

1. **Use appropriate batch sizes**: 50-100 for most cases
2. **Adjust worker count**: Match your CPU cores
3. **Use quality config for important data**: Better extraction accuracy
4. **Use fast config for bulk processing**: Faster but less accurate
5. **Monitor memory usage**: Reduce batch size if needed

## 🔄 Migration from Old Pipeline

The enhanced pipeline is backward compatible. To migrate:

1. Replace `CochraneProcessingPipeline` with `EnhancedCochranePipeline`
2. Use configuration objects instead of hard-coded parameters
3. Add progress callbacks for better monitoring
4. Use batch processing for multiple files

```python
# Old way
from src.preprocessing import CochraneProcessingPipeline
pipeline = CochraneProcessingPipeline()
result = pipeline.process_file(file_path)

# New way
from src.preprocessing import EnhancedCochranePipeline
pipeline = EnhancedCochranePipeline()
result = pipeline.process_single_file(file_path, output_path)
```

## 📈 Future Enhancements

- Support for additional output formats (Parquet, CSV)
- Real-time web dashboard for monitoring
- Automatic configuration optimization
- Integration with cloud storage services
- Advanced error recovery mechanisms

---

For more examples and detailed documentation, see the `examples/` directory and the source code documentation.
