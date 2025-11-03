"""
Retrieval system for Cochrane RAG using OpenAI embeddings.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from weaviate.classes.query import Filter, MetadataQuery
from src.indexing.weaviate_client import WeaviateManager
from src.retrieving.embedder import OpenAIEmbedder


@dataclass
class RetrievalResult:
    """Single retrieval result."""

    chunk_id: str
    document_id: str
    level: str
    content: str
    section_name: str
    subsection_name: str
    is_statistical: bool
    distance: float
    
    title: str = ""
    url: str = ""
    doi: str = ""
    topic_name: str = ""
    quality_grade: str = ""
    
    # Hierarchical context (for Stage 3: Context Assembly)
    parent_chunk_id: str = ""
    enriched_content: str = ""
    
    # Query decomposition metadata
    sub_query_intent: str = ""
    sub_query_priority: int = 0

    def __str__(self):
        return f"""
Result:
  Level: {self.level}
  Section: {self.section_name}
  Topic: {self.topic_name}
  Quality: {self.quality_grade}
  Statistical: {self.is_statistical}
  Distance: {self.distance:.4f}
  Content: {self.content[:200]}...
"""


class CochraneRetriever:
    """Retrieval system for Cochrane medical documents."""

    def __init__(self):
        """Initialize retriever with Weaviate and OpenAI embedder."""
        print("Initializing Cochrane Retriever...")
        self.weaviate_manager = WeaviateManager()
        self.collection = self.weaviate_manager.client.collections.get("CochraneChunk")
        self.embedder = OpenAIEmbedder()
        print("✅ Retriever ready!")

    def search(
        self,
        query: str,
        limit: int = 5,
        level: Optional[str] = None,
        topic: Optional[str] = None,
        quality_grade: Optional[str] = None,
        statistical_only: bool = False,
        section: Optional[str] = None,
        use_hybrid: bool = True,
    ) -> List[RetrievalResult]:
        """
        Search for relevant chunks using hybrid search (semantic + BM25).

        Args:
            query: Natural language query
            limit: Maximum number of results
            level: Filter by chunk level (DOCUMENT, SECTION, SUBSECTION, PARAGRAPH)
            topic: Filter by medical topic
            quality_grade: Filter by quality grade (A, B, C)
            statistical_only: Only return chunks with statistical data
            section: Filter by section name (methods, results, etc.)
            use_hybrid: Use hybrid search (semantic + BM25) vs semantic only

        Returns:
            List of retrieval results
        """
        print(f"🔍 Searching for: '{query}'")
        
        # Build filters
        filters = self._build_filters(
            level=level,
            topic=topic,
            quality_grade=quality_grade,
            statistical_only=statistical_only,
            section=section,
        )

        # Execute hybrid search (semantic + BM25) or semantic only
        if use_hybrid:
            query_vector = self.embedder.encode(query)
            response = self.collection.query.hybrid(
                query=query,
                vector=query_vector,
                limit=limit,
                alpha=0.7,  # 70% semantic, 30% BM25 (expert strategy)
                filters=filters,
                return_metadata=MetadataQuery(distance=True, score=True),
            )
        else:
            query_vector = self.embedder.encode(query)
            response = self.collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                filters=filters,
                return_metadata=MetadataQuery(distance=True),
            )

        # Convert to RetrievalResult objects
        results = []
        for obj in response.objects:
            props = obj.properties
            # Handle both distance (vector search) and score (hybrid search)
            metadata = obj.metadata if obj.metadata else None
            distance = 0.0
            if metadata:
                # Hybrid search provides score (higher is better), convert to distance
                if hasattr(metadata, 'score') and metadata.score is not None:
                    distance = 1.0 - metadata.score  # Convert score to distance
                elif hasattr(metadata, 'distance') and metadata.distance is not None:
                    distance = metadata.distance
                elif hasattr(metadata, 'distance') and hasattr(metadata, 'score'):
                    # If distance is None but score exists, use score
                    if metadata.distance is None and metadata.score is not None:
                        distance = 1.0 - metadata.score
            
            result = RetrievalResult(
                chunk_id=props.get("chunk_id", ""),
                document_id=props.get("document_id", ""),
                level=props.get("level", ""),
                content=props.get("content", ""),
                section_name=props.get("section_name", ""),
                subsection_name=props.get("subsection_name", ""),
                is_statistical=props.get("is_statistical", False),
                distance=distance,
                parent_chunk_id=props.get("parent_chunk_id", ""),
            )
            results.append(result)

        # Enrich with document metadata
        doc_ids = list(set(r.document_id for r in results))
        metadata_map = self.weaviate_manager.get_batch_document_metadata(doc_ids)
        
        for result in results:
            if result.document_id in metadata_map:
                meta = metadata_map[result.document_id]
                result.title = meta.get("title", "")
                result.url = meta.get("url", "")
                result.doi = meta.get("doi", "")
                result.topic_name = meta.get("topic_name", "")
                result.quality_grade = meta.get("quality_grade", "")
        
        # STAGE 3: Enrich with hierarchical context (as per plan)
        results = self._enrich_with_hierarchical_context(results)

        # Post-filter by metadata (topic, quality_grade)
        results = self._post_filter_by_metadata(results, topic=topic, quality_grade=quality_grade)
        
        if len(results) > limit:
            results = results[:limit]

        print(f"✅ Found {len(results)} results")
        return results

    def search_by_section(
        self, query: str, section: str, limit: int = 5
    ) -> List[RetrievalResult]:
        """
        Search within a specific section (e.g., 'methods', 'results').

        Args:
            query: Natural language query
            section: Section name to search in
            limit: Maximum number of results

        Returns:
            List of retrieval results
        """
        return self.search(query=query, limit=limit, section=section)

    def search_statistical(self, query: str, limit: int = 5) -> List[RetrievalResult]:
        """
        Search for chunks containing statistical data.

        Args:
            query: Natural language query
            limit: Maximum number of results

        Returns:
            List of retrieval results with statistical content
        """
        return self.search(query=query, limit=limit, statistical_only=True)

    def search_by_topic(
        self, query: str, topic: str, limit: int = 5
    ) -> List[RetrievalResult]:
        """
        Search within a specific medical topic.

        Args:
            query: Natural language query
            topic: Medical topic name
            limit: Maximum number of results

        Returns:
            List of retrieval results
        """
        return self.search(query=query, limit=limit, topic=topic)

    def search_high_quality(self, query: str, limit: int = 5) -> List[RetrievalResult]:
        """
        Search only in high-quality (Grade A) reviews.

        Args:
            query: Natural language query
            limit: Maximum number of results

        Returns:
            List of retrieval results from Grade A reviews
        """
        return self.search(query=query, limit=limit, quality_grade="A")

    def _build_filters(
        self,
        level: Optional[str] = None,
        topic: Optional[str] = None,
        quality_grade: Optional[str] = None,
        statistical_only: bool = False,
        section: Optional[str] = None,
    ) -> Optional[Filter]:
        """Build Weaviate filter from search parameters."""
        filters = []

        if level:
            filters.append(Filter.by_property("level").equal(level))

        if statistical_only:
            filters.append(Filter.by_property("is_statistical").equal(True))

        if section:
            filters.append(Filter.by_property("section_name").equal(section))

        if not filters:
            return None

        combined_filter = filters[0]
        for f in filters[1:]:
            combined_filter = combined_filter & f

        return combined_filter
    
    def _enrich_with_hierarchical_context(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Enrich results with hierarchical context from parent chunks.
        
        Stage 3 Context Assembly as per plan:
        - Include related sections (abstract + results + conclusions)
        - Preserve hierarchical relationships
        - Add metadata context
        """
        for result in results:
            # For PARAGRAPH level, enrich with parent section context
            if result.level == "PARAGRAPH" and result.parent_chunk_id:
                parent_chunk = self._get_chunk_by_id(result.parent_chunk_id)
                if parent_chunk:
                    # Build enriched content with hierarchical context
                    enriched_parts = []
                    
                    # Add parent section context if available
                    if parent_chunk.get("section_name"):
                        enriched_parts.append(f"## {parent_chunk['section_name']}")
                    
                    # Add the actual content
                    enriched_parts.append(result.content)
                    
                    # Add statistical context if parent has it
                    if parent_chunk.get("has_statistical_data"):
                        enriched_parts.append("\n[Contains statistical analysis]")
                    
                    result.enriched_content = "\n\n".join(enriched_parts)
                else:
                    # Fallback: use content without parent context
                    result.enriched_content = result.content
            
            # For SUBSECTION level, just use the content with section header
            elif result.level == "SUBSECTION":
                enriched_parts = []
                if result.section_name:
                    enriched_parts.append(f"## {result.section_name}")
                if result.subsection_name:
                    enriched_parts.append(f"### {result.subsection_name}")
                enriched_parts.append(result.content)
                result.enriched_content = "\n\n".join(enriched_parts)
            
            # For DOCUMENT and SECTION levels, content is already contextual
            else:
                result.enriched_content = result.content
        
        return results
    
    def _get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a chunk by its ID from Weaviate."""
        try:
            response = self.collection.query.fetch_objects(
                filters=Filter.by_property("chunk_id").equal(chunk_id),
                limit=1
            )
            if response.objects:
                return response.objects[0].properties
        except Exception as e:
            print(f"Warning: Could not fetch chunk {chunk_id}: {e}")
        return None
    
    def _post_filter_by_metadata(
        self,
        results: List[RetrievalResult],
        topic: Optional[str] = None,
        quality_grade: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """Post-filter results by metadata fields."""
        if not topic and not quality_grade:
            return results
        
        filtered = []
        for result in results:
            if topic and result.topic_name != topic:
                continue
            if quality_grade and result.quality_grade != quality_grade:
                continue
            filtered.append(result)
        
        return filtered

    def format_results(self, results: List[RetrievalResult]) -> str:
        """
        Format results for display.

        Args:
            results: List of retrieval results

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 80)
        output.append(f"RETRIEVAL RESULTS ({len(results)} found)")
        output.append("=" * 80)

        for i, result in enumerate(results, 1):
            output.append(
                f"\n[{i}] Level: {result.level} | Distance: {result.distance:.4f}"
            )
            output.append(f"    Section: {result.section_name}")
            output.append(f"    Topic: {result.topic_name}")
            output.append(f"    Quality: {result.quality_grade}")
            if result.is_statistical:
                output.append(f"    📊 Contains statistical data")
            output.append(f"    Content: {result.content[:300]}...")
            output.append("")

        return "\n".join(output)

    def close(self):
        """Close Weaviate connection."""
        self.weaviate_manager.close()
