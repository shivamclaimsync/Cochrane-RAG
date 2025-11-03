from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class ChunkLevel(Enum):
    DOCUMENT = 1
    SECTION = 2
    SUBSECTION = 3
    PARAGRAPH = 4


@dataclass
class BaseChunk:
    chunk_id: str
    document_id: str
    level: ChunkLevel
    content: str
    title: str = ""


@dataclass
class DocumentChunk(BaseChunk):
    quality_grade: str = ""
    topic_name: str = ""
    authors: List[str] = field(default_factory=list)
    pico_summary: Dict[str, List[str]] = field(default_factory=dict)
    medical_entities: Dict[str, List[str]] = field(default_factory=dict)
    extraction_date: str = ""
    url: str = ""


@dataclass
class SectionChunk(BaseChunk):
    section_name: str = ""
    subsection_count: int = 0
    has_statistical_data: bool = False


@dataclass
class SubsectionChunk(BaseChunk):
    section_name: str = ""
    subsection_name: str = ""
    parent_section_id: str = ""


@dataclass
class ParagraphChunk(BaseChunk):
    section_name: str = ""
    subsection_name: Optional[str] = None
    paragraph_index: int = 0
    parent_chunk_id: str = ""
    is_statistical: bool = False


@dataclass
class ChunkCollection:
    document_id: str
    document_chunks: List[DocumentChunk] = field(default_factory=list)
    section_chunks: List[SectionChunk] = field(default_factory=list)
    subsection_chunks: List[SubsectionChunk] = field(default_factory=list)
    paragraph_chunks: List[ParagraphChunk] = field(default_factory=list)
    
    @property
    def total_chunks(self) -> int:
        return (len(self.document_chunks) + 
                len(self.section_chunks) + 
                len(self.subsection_chunks) + 
                len(self.paragraph_chunks))
    
    def get_all_chunks(self) -> List[BaseChunk]:
        return (self.document_chunks + 
                self.section_chunks + 
                self.subsection_chunks + 
                self.paragraph_chunks)


@dataclass
class ProcessingHistory:
    document_id: str
    processed_date: str
    chunk_count: int
    status: str

