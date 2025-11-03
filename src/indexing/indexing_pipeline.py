import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from src.core.data_models import ProcessedDocument, EnrichedMetadata, ExtractedSections, SectionContent, PicoElements, MedicalEntities, QualityGrade
from src.indexing.chunker import MultiLevelChunker
from src.indexing.weaviate_client import WeaviateManager
from src.indexing.config import PathConfig, ChunkingConfig


class IndexingPipeline:
    
    def __init__(self):
        self.chunker = MultiLevelChunker(min_paragraph_length=ChunkingConfig.MIN_PARAGRAPH_LENGTH)
        self.weaviate_manager = WeaviateManager()
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_chunks': 0
        }
    
    def index_processed_documents(self, processed_dir: Path, skip_processed: bool = True, limit: Optional[int] = None):
        if not processed_dir.exists():
            raise FileNotFoundError(f"Processed data directory not found: {processed_dir}")
        
        json_files = list(processed_dir.glob('processed_*.json'))
        
        if limit:
            json_files = json_files[:limit]
        
        print(f"Found {len(json_files)} processed documents")
        
        for idx, json_file in enumerate(json_files, 1):
            print(f"\n[{idx}/{len(json_files)}] Processing: {json_file.name}")
            
            try:
                processed_doc = self._load_processed_document(json_file)
                document_id = processed_doc.metadata.doi
                
                if skip_processed and self.weaviate_manager.check_if_processed(document_id):
                    print(f"  ✓ Already processed, skipping")
                    self.stats['skipped'] += 1
                    continue
                
                start_time = time.time()
                
                chunk_collection = self.chunker.chunk_document(processed_doc)
                
                print(f"  → Created {chunk_collection.total_chunks} chunks")
                print(f"    - Level 1 (Document): {len(chunk_collection.document_chunks)}")
                print(f"    - Level 2 (Section): {len(chunk_collection.section_chunks)}")
                print(f"    - Level 3 (Subsection): {len(chunk_collection.subsection_chunks)}")
                print(f"    - Level 4 (Paragraph): {len(chunk_collection.paragraph_chunks)}")
                
                metadata_success = self.weaviate_manager.insert_document_metadata(processed_doc)
                chunks_success = self.weaviate_manager.insert_chunks(chunk_collection)
                
                if metadata_success and chunks_success:
                    self.weaviate_manager.mark_as_processed(document_id, chunk_collection.total_chunks)
                    self.stats['successful'] += 1
                    self.stats['total_chunks'] += chunk_collection.total_chunks
                    
                    elapsed = time.time() - start_time
                    print(f"  ✓ Successfully indexed in {elapsed:.2f}s")
                else:
                    self.stats['failed'] += 1
                    print(f"  ✗ Failed to insert chunks")
                
                self.stats['total_processed'] += 1
                
            except Exception as e:
                print(f"  ✗ Error processing document: {e}")
                self.stats['failed'] += 1
        
        self._print_summary()
    
    def batch_index(self, batch_size: int = 10):
        processed_dir = PathConfig.PROCESSED_DATA_DIR
        
        json_files = list(processed_dir.glob('processed_*.json'))
        print(f"Found {len(json_files)} processed documents")
        
        # First pass: Extract document IDs from all files
        print("\nExtracting document IDs from files...")
        file_to_doc_id = {}
        for json_file in json_files:
            try:
                document_id = self._extract_document_id(json_file)
                if document_id:
                    file_to_doc_id[json_file] = document_id
            except Exception as e:
                print(f"Error extracting document ID from {json_file.name}: {e}")
                continue
        
        print(f"Extracted {len(file_to_doc_id)} document IDs")
        
        # Batch check: Get all processed document IDs from Weaviate at once
        print("\nChecking processed documents in Weaviate...")
        processed_doc_ids = self.weaviate_manager.get_all_processed_document_ids()
        print(f"Found {len(processed_doc_ids)} already processed documents in Weaviate")
        
        # Filter: Only process files that haven't been processed
        files_to_process = [
            json_file for json_file, doc_id in file_to_doc_id.items()
            if doc_id not in processed_doc_ids
        ]
        
        skipped_count = len(json_files) - len(files_to_process)
        if skipped_count > 0:
            print(f"Skipping {skipped_count} already processed documents")
            self.stats['skipped'] += skipped_count
        
        if not files_to_process:
            print("All documents have already been processed!")
            self._print_summary()
            return
        
        print(f"\nProcessing {len(files_to_process)} unprocessed documents in batches of {batch_size}")
        
        # Second pass: Process only unprocessed files in batches
        for i in range(0, len(files_to_process), batch_size):
            batch = files_to_process[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} files)")
            
            for json_file in batch:
                try:
                    processed_doc = self._load_processed_document(json_file)
                    document_id = processed_doc.metadata.doi
                    
                    chunk_collection = self.chunker.chunk_document(processed_doc)
                    metadata_success = self.weaviate_manager.insert_document_metadata(processed_doc)
                    chunks_success = self.weaviate_manager.insert_chunks(chunk_collection)
                    
                    if metadata_success and chunks_success:
                        self.weaviate_manager.mark_as_processed(document_id, chunk_collection.total_chunks)
                        self.stats['successful'] += 1
                        self.stats['total_chunks'] += chunk_collection.total_chunks
                    else:
                        self.stats['failed'] += 1
                    
                    self.stats['total_processed'] += 1
                    
                except Exception as e:
                    print(f"Error processing {json_file.name}: {e}")
                    self.stats['failed'] += 1
        
        self._print_summary()
    
    def _extract_document_id(self, json_file: Path) -> Optional[str]:
        """
        Extract document ID (DOI) from a JSON file without loading the full document.
        This is more efficient for batch checking.
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('metadata', {}).get('doi')
        except Exception as e:
            print(f"Error extracting document ID from {json_file.name}: {e}")
            return None
    
    def _load_processed_document(self, json_file: Path) -> ProcessedDocument:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata_dict = data['metadata']
        pico_dict = metadata_dict['pico_elements']
        entities_dict = metadata_dict['medical_entities']
        
        pico_elements = PicoElements(
            population=pico_dict.get('population', []),
            intervention=pico_dict.get('intervention', []),
            comparison=pico_dict.get('comparison', []),
            outcome=pico_dict.get('outcome', [])
        )
        
        medical_entities = MedicalEntities(
            conditions=entities_dict.get('conditions', []),
            drugs=entities_dict.get('drugs', []),
            procedures=entities_dict.get('procedures', []),
            outcomes=entities_dict.get('outcomes', [])
        )
        
        # Reconstruct full_content from sections if not present
        full_content = metadata_dict.get('full_content')
        if not full_content:
            full_content_parts = []
            for section_name, section_data in data.get('sections', {}).items():
                section_text = section_data.get('content', '')
                # Add subsection content
                for sub_name, sub_content in section_data.get('subsections', {}).items():
                    section_text += f"\n\n### {sub_name}\n{sub_content}"
                full_content_parts.append(f"## {section_name}\n{section_text}")
            full_content = '\n\n'.join(full_content_parts) if full_content_parts else ''
        
        metadata = EnrichedMetadata(
            source_file=metadata_dict['source_file'],
            title=metadata_dict['title'],
            doi=metadata_dict['doi'],
            authors=metadata_dict['authors'],
            url=metadata_dict.get('url', ''),
            topic_name=metadata_dict['topic_name'],
            quality_grade=QualityGrade(metadata_dict['quality_grade']),
            extraction_date=metadata_dict['extraction_date'],
            publication_date=metadata_dict.get('publication_date', metadata_dict['extraction_date']),
            content_length=metadata_dict['content_length'],
            pico_elements=pico_elements,
            medical_entities=medical_entities,
            sections_extracted=metadata_dict['sections_extracted'],
            section_count=metadata_dict['section_count'],
            subsection_count=metadata_dict['subsection_count'],
            full_content=full_content or ''
        )
        
        sections_dict = {}
        for section_name, section_data in data['sections'].items():
            section_content = SectionContent(
                name=section_data.get('name', section_name),
                content=section_data['content'],
                subsections=section_data.get('subsections', {})
            )
            sections_dict[section_name] = section_content
        
        sections = ExtractedSections(
            sections=sections_dict,
            section_count=metadata.section_count,
            subsection_count=metadata.subsection_count
        )
        
        return ProcessedDocument(metadata=metadata, sections=sections)
    
    def _print_summary(self):
        print("\n" + "="*60)
        print("INDEXING SUMMARY")
        print("="*60)
        print(f"Total Processed: {self.stats['total_processed']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Total Chunks Created: {self.stats['total_chunks']}")
        
        weaviate_stats = self.weaviate_manager.get_processing_stats()
        if weaviate_stats:
            print(f"\nWeaviate Statistics:")
            print(f"  Total Chunks in DB: {weaviate_stats.get('total_chunks', 0)}")
            print(f"  Total Documents Processed: {weaviate_stats.get('total_documents_processed', 0)}")
            if 'chunks_by_level' in weaviate_stats:
                print(f"  Chunks by Level:")
                for level, count in weaviate_stats['chunks_by_level'].items():
                    print(f"    - {level}: {count}")
        print("="*60)
    
    def close(self):
        self.weaviate_manager.close()

