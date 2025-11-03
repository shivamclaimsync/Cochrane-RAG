import re
from typing import List
from src.core.data_models import ProcessedDocument
from src.core.chunk_models import (
    ChunkLevel, ChunkCollection, DocumentChunk, 
    SectionChunk, SubsectionChunk, ParagraphChunk
)


class MultiLevelChunker:
    
    def __init__(self, min_paragraph_length: int = 50):
        self.min_paragraph_length = min_paragraph_length
    
    def chunk_document(self, processed_doc: ProcessedDocument) -> ChunkCollection:
        document_id = processed_doc.metadata.doi
        
        collection = ChunkCollection(document_id=document_id)
        
        collection.document_chunks = [self._create_document_chunk(processed_doc)]
        collection.section_chunks = self._create_section_chunks(processed_doc)
        collection.subsection_chunks = self._create_subsection_chunks(processed_doc)
        collection.paragraph_chunks = self._create_paragraph_chunks(processed_doc)
        
        return collection
    
    def _create_document_chunk(self, doc: ProcessedDocument) -> DocumentChunk:
        metadata = doc.metadata
        
        pico_summary_text = self._format_pico_summary(metadata.pico_elements)
        entities_text = self._format_medical_entities(metadata.medical_entities)
        
        content = f"""Title: {metadata.title}

Topic: {metadata.topic_name}
Quality Grade: {metadata.quality_grade}
Authors: {', '.join(metadata.authors[:5])}

{pico_summary_text}

{entities_text}"""
        
        return DocumentChunk(
            chunk_id=f"{metadata.doi}_L1_0",
            document_id=metadata.doi,
            level=ChunkLevel.DOCUMENT,
            content=content,
            title=metadata.title,
            quality_grade=metadata.quality_grade,
            topic_name=metadata.topic_name,
            authors=metadata.authors,
            pico_summary={
                'population': metadata.pico_elements.population,
                'intervention': metadata.pico_elements.intervention,
                'comparison': metadata.pico_elements.comparison,
                'outcome': metadata.pico_elements.outcome
            },
            medical_entities={
                'conditions': metadata.medical_entities.conditions,
                'drugs': metadata.medical_entities.drugs,
                'procedures': metadata.medical_entities.procedures,
                'outcomes': metadata.medical_entities.outcomes
            },
            extraction_date=metadata.extraction_date,
            url=metadata.url
        )
    
    def _create_section_chunks(self, doc: ProcessedDocument) -> List[SectionChunk]:
        chunks = []
        document_id = doc.metadata.doi
        title = doc.metadata.title
        
        for idx, (section_name, section_data) in enumerate(doc.sections.sections.items()):
            content = section_data.content
            
            if not content or len(content.strip()) < self.min_paragraph_length:
                continue
            
            has_statistical_data = self._detect_statistical_content(content)
            
            chunk = SectionChunk(
                chunk_id=f"{document_id}_L2_{idx}",
                document_id=document_id,
                level=ChunkLevel.SECTION,
                content=content,
                title=title,
                section_name=section_name,
                subsection_count=len(section_data.subsections),
                has_statistical_data=has_statistical_data
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_subsection_chunks(self, doc: ProcessedDocument) -> List[SubsectionChunk]:
        chunks = []
        document_id = doc.metadata.doi
        title = doc.metadata.title
        global_idx = 0
        
        for section_name, section_data in doc.sections.sections.items():
            parent_section_id = f"{document_id}_L2_{list(doc.sections.sections.keys()).index(section_name)}"
            
            for subsection_name, subsection_content in section_data.subsections.items():
                if not subsection_content or len(subsection_content.strip()) < self.min_paragraph_length:
                    continue
                
                chunk = SubsectionChunk(
                    chunk_id=f"{document_id}_L3_{global_idx}",
                    document_id=document_id,
                    level=ChunkLevel.SUBSECTION,
                    content=subsection_content,
                    title=title,
                    section_name=section_name,
                    subsection_name=subsection_name,
                    parent_section_id=parent_section_id
                )
                chunks.append(chunk)
                global_idx += 1
        
        return chunks
    
    def _create_paragraph_chunks(self, doc: ProcessedDocument) -> List[ParagraphChunk]:
        chunks = []
        document_id = doc.metadata.doi
        title = doc.metadata.title
        global_idx = 0
        
        for section_name, section_data in doc.sections.sections.items():
            section_idx = list(doc.sections.sections.keys()).index(section_name)
            parent_section_id = f"{document_id}_L2_{section_idx}"
            
            paragraphs = self._split_into_paragraphs(section_data.content)
            
            for para_idx, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) < self.min_paragraph_length:
                    continue
                
                is_statistical = self._detect_statistical_content(paragraph)
                
                chunk = ParagraphChunk(
                    chunk_id=f"{document_id}_L4_{global_idx}",
                    document_id=document_id,
                    level=ChunkLevel.PARAGRAPH,
                    content=paragraph,
                    title=title,
                    section_name=section_name,
                    subsection_name=None,
                    paragraph_index=para_idx,
                    parent_chunk_id=parent_section_id,
                    is_statistical=is_statistical
                )
                chunks.append(chunk)
                global_idx += 1
        
        return chunks
    
    def _format_pico_summary(self, pico) -> str:
        parts = []
        
        if pico.population:
            parts.append(f"Population: {', '.join(pico.population[:3])}")
        if pico.intervention:
            parts.append(f"Intervention: {', '.join(pico.intervention[:3])}")
        if pico.comparison:
            parts.append(f"Comparison: {', '.join(pico.comparison[:2])}")
        if pico.outcome:
            parts.append(f"Outcome: {', '.join(pico.outcome[:3])}")
        
        return '\n'.join(parts) if parts else "PICO elements not specified"
    
    def _format_medical_entities(self, entities) -> str:
        parts = []
        
        if entities.conditions:
            parts.append(f"Conditions: {', '.join(entities.conditions[:5])}")
        if entities.drugs:
            parts.append(f"Drugs: {', '.join(entities.drugs[:5])}")
        if entities.procedures:
            parts.append(f"Procedures: {', '.join(entities.procedures[:5])}")
        
        return '\n'.join(parts) if parts else "Medical entities not specified"
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        paragraphs = re.split(r'\n\n+', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _detect_statistical_content(self, text: str) -> bool:
        statistical_patterns = [
            r'\bp\s*[<>=]\s*0\.\d+',
            r'\b95%\s*CI\b',
            r'\bconfidence interval\b',
            r'\brisk ratio\b',
            r'\bodds ratio\b',
            r'\bmean difference\b',
            r'\bMD\b.*\bCI\b',
            r'\bRR\b.*\bCI\b',
            r'\bOR\b.*\bCI\b',
            r'\bp-value\b'
        ]
        
        for pattern in statistical_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

