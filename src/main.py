"""
Main entry point for Cochrane RAG system preprocessing pipeline.

This module provides the main interface for running the preprocessing pipeline.
"""

import argparse
from pathlib import Path
from .preprocessing.pipeline import CochraneProcessingPipeline


def main():
    """Main entry point for the preprocessing pipeline."""
    parser = argparse.ArgumentParser(
        description='Cochrane RAG System - Data Ingestion and Preprocessing Pipeline'
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        default='raw/json',
        help='Input directory containing Cochrane JSON files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='processed_data',
        help='Output directory for processed files'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='processing_logs',
        help='Directory for processing logs'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of files to process (for testing)'
    )
    
    parser.add_argument(
        '--single-file',
        type=str,
        help='Process a single file instead of directory'
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = CochraneProcessingPipeline()
    
    if args.single_file:
        # Process single file
        file_path = Path(args.single_file)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return
        
        print(f"Processing single file: {file_path.name}")
        result = pipeline.process_file(file_path)
        
        if result.success:
            print("✅ Processing successful!")
            if result.document:
                print(f"   Sections extracted: {result.document.metadata.section_count}")
                print(f"   Subsections extracted: {result.document.metadata.subsection_count}")
                print(f"   Processing time: {result.processing_time:.2f}s")
        else:
            print("❌ Processing failed!")
            for error in result.errors:
                print(f"   Error: {error}")
    
    else:
        # Process directory
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        log_dir = Path(args.log_dir)
        
        if not input_dir.exists():
            print(f"Error: Input directory {input_dir} does not exist")
            return
        
        print(f"Processing directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Log directory: {log_dir}")
        if args.limit:
            print(f"Processing limit: {args.limit} files")
        
        # Run pipeline
        report = pipeline.process_directory(input_dir, output_dir, log_dir, args.limit)
        
        # Print results
        print("\n" + "="*80)
        print("📊 PROCESSING COMPLETE")
        print("="*80)
        
        summary = report['processing_summary']
        print(f"Total Processed: {summary['total_processed']}")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Average Processing Time: {summary['average_processing_time']:.2f}s")
        
        stats = report['statistics']
        print(f"\n📈 Content Statistics:")
        print(f"Total Sections: {stats['total_sections']}")
        print(f"Total Subsections: {stats['total_subsections']}")
        print(f"Average Sections per Document: {stats['average_sections_per_document']:.1f}")
        print(f"Average Subsections per Document: {stats['average_subsections_per_document']:.1f}")
        
        quality = report['quality_metrics']
        print(f"\n🎯 Quality Metrics:")
        print(f"Total Errors: {quality['total_errors']}")
        print(f"Error Rate: {quality['error_rate']:.1%}")
        if 'total_warnings' in quality:
            print(f"Total Warnings: {quality['total_warnings']}")
            print(f"Warning Rate: {quality['warning_rate']:.1%}")
        
        if report['common_issues']['errors']:
            print(f"\n⚠️  Common Errors:")
            for error_type, count in list(report['common_issues']['errors'].items())[:3]:
                print(f"   {error_type}: {count}")
        
        if report['common_issues']['warnings']:
            print(f"\n⚠️  Common Warnings:")
            for warning_type, count in list(report['common_issues']['warnings'].items())[:3]:
                print(f"   {warning_type}: {count}")
        
        print("="*80)


if __name__ == '__main__':
    main()
