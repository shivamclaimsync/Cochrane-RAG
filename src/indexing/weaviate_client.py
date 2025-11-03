from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import json
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter
from weaviate.classes.init import AdditionalConfig, Timeout
from src.core.chunk_models import BaseChunk, ChunkCollection, ChunkLevel
from src.indexing.config import WeaviateConfig


class WeaviateManager:

    def __init__(self):
        self.config = WeaviateConfig()
        self.client = None
        self._connect()

    def _connect(self):
        if not self.config.URL or not self.config.API_KEY:
            raise ValueError(
                "WEAVIATE_URL and WEAVIATE_API_KEY must be set in .env file"
            )

        # Get OpenAI API key for embeddings
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set in .env file for OpenAI embeddings"
            )

        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.config.URL,
            auth_credentials=weaviate.auth.AuthApiKey(self.config.API_KEY),
            headers={"X-OpenAI-Api-Key": openai_api_key},
            additional_config=AdditionalConfig(
                timeout=Timeout(init=30, query=60, insert=120)
            ),
        )

        if not self.client.is_ready():
            raise ConnectionError("Failed to connect to Weaviate")

        self._create_schema()

    def _create_schema(self):
        """Create collections with OpenAI vectorizer if they don't exist."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set in .env file for OpenAI embeddings"
            )

        try:
            documents_collection = self.client.collections.get(
                self.config.COLLECTION_DOCUMENTS
            )
            print(f"✓ Collection {self.config.COLLECTION_DOCUMENTS} already exists")
        except:
            print(f"Creating collection {self.config.COLLECTION_DOCUMENTS}...")
            self.client.collections.create(
                name=self.config.COLLECTION_DOCUMENTS,
                properties=[
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="url", data_type=DataType.TEXT),
                    Property(name="doi", data_type=DataType.TEXT),
                    Property(name="authors", data_type=DataType.TEXT_ARRAY),
                    Property(name="topic_name", data_type=DataType.TEXT),
                    Property(name="quality_grade", data_type=DataType.TEXT),
                    Property(name="extraction_date", data_type=DataType.TEXT),
                    Property(name="publication_date", data_type=DataType.TEXT),
                    Property(name="content_length", data_type=DataType.INT),
                    Property(name="pico_summary", data_type=DataType.TEXT),
                    Property(name="section_count", data_type=DataType.INT),
                    Property(name="subsection_count", data_type=DataType.INT),
                ],
                vectorizer_config=Configure.Vectorizer.none(),
                vector_config=Configure.Vectorizer.none(),
            )
            print(f"✅ Collection {self.config.COLLECTION_DOCUMENTS} created")

        try:
            chunks_collection = self.client.collections.get(
                self.config.COLLECTION_CHUNKS
            )
            print(f"✓ Collection {self.config.COLLECTION_CHUNKS} already exists")
        except:
            print(f"Creating collection {self.config.COLLECTION_CHUNKS}...")
            self.client.collections.create(
                name=self.config.COLLECTION_CHUNKS,
                properties=[
                    Property(name="chunk_id", data_type=DataType.TEXT),
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="level", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="section_name", data_type=DataType.TEXT),
                    Property(name="subsection_name", data_type=DataType.TEXT),
                    Property(name="paragraph_index", data_type=DataType.INT),
                    Property(name="is_statistical", data_type=DataType.BOOL),
                    Property(name="parent_chunk_id", data_type=DataType.TEXT),
                    Property(name="subsection_count", data_type=DataType.INT),
                    Property(name="has_statistical_data", data_type=DataType.BOOL),
                ],
                vectorizer_config=Configure.Vectorizer.none(),
                vector_config=Configure.Vectorizer.none(),
            )
            print(f"✅ Collection {self.config.COLLECTION_CHUNKS} created")

        try:
            history_collection = self.client.collections.get(
                self.config.COLLECTION_HISTORY
            )
        except:
            self.client.collections.create(
                name=self.config.COLLECTION_HISTORY,
                properties=[
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="processed_date", data_type=DataType.TEXT),
                    Property(name="chunk_count", data_type=DataType.INT),
                    Property(name="status", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none(),
                vector_config=Configure.Vectorizer.none(),
            )

    def check_if_processed(self, document_id: str) -> bool:
        try:
            history_collection = self.client.collections.get(
                self.config.COLLECTION_HISTORY
            )

            response = history_collection.query.fetch_objects(
                filters=Filter.by_property("document_id").equal(document_id), limit=1
            )

            return len(response.objects) > 0
        except Exception as e:
            print(f"Error checking processing history: {e}")
            return False

    def get_all_processed_document_ids(self) -> set[str]:
        """
        Get all processed document IDs from the history collection.
        Returns a set of document IDs that have already been processed.
        """
        try:
            history_collection = self.client.collections.get(
                self.config.COLLECTION_HISTORY
            )
            
            # Fetch all objects from the history collection
            all_processed = history_collection.query.fetch_objects(limit=None)
            
            # Extract document_id from each object
            processed_ids = set()
            for obj in all_processed.objects:
                props = obj.properties
                if props and "document_id" in props:
                    processed_ids.add(props["document_id"])
            
            return processed_ids
        except Exception as e:
            print(f"Error getting processed document IDs: {e}")
            return set()

    def insert_document_metadata(self, processed_doc) -> bool:
        try:
            from src.core.data_models import ProcessedDocument
            import json
            
            documents_collection = self.client.collections.get(
                self.config.COLLECTION_DOCUMENTS
            )
            
            metadata = processed_doc.metadata
            
            # Generate URL from DOI if not provided
            url = metadata.url
            if not url and metadata.doi:
                url = f'https://www.cochranelibrary.com/cdsr/doi/{metadata.doi}/full'
            
            document_obj = {
                "document_id": metadata.doi,
                "title": metadata.title,
                "url": url,
                "doi": metadata.doi,
                "authors": metadata.authors,
                "topic_name": metadata.topic_name,
                "quality_grade": metadata.quality_grade.value if hasattr(metadata.quality_grade, 'value') else str(metadata.quality_grade),
                "extraction_date": metadata.extraction_date,
                "publication_date": metadata.publication_date,
                "content_length": metadata.content_length,
                "pico_summary": json.dumps({
                    'population': metadata.pico_elements.population,
                    'intervention': metadata.pico_elements.intervention,
                    'comparison': metadata.pico_elements.comparison,
                    'outcome': metadata.pico_elements.outcome
                }),
                "section_count": metadata.section_count,
                "subsection_count": metadata.subsection_count,
            }
            
            documents_collection.data.insert(document_obj)
            return True
        except Exception as e:
            print(f"Error inserting document metadata: {e}")
            return False
    
    def insert_chunks(self, chunk_collection: ChunkCollection) -> bool:
        try:
            from src.retrieving.embedder import OpenAIEmbedder
            
            chunks_collection = self.client.collections.get(
                self.config.COLLECTION_CHUNKS
            )

            all_chunks = chunk_collection.get_all_chunks()
            
            embedder = OpenAIEmbedder()

            with chunks_collection.batch.dynamic() as batch:
                for chunk in all_chunks:
                    weaviate_obj = self._chunk_to_weaviate_object(chunk)
                    vector = embedder.encode(chunk.content)
                    batch.add_object(properties=weaviate_obj, vector=vector)

            return True
        except Exception as e:
            print(f"Error inserting chunks: {e}")
            return False

    def mark_as_processed(self, document_id: str, chunk_count: int):
        try:
            history_collection = self.client.collections.get(
                self.config.COLLECTION_HISTORY
            )

            history_collection.data.insert(
                {
                    "document_id": document_id,
                    "processed_date": datetime.now().isoformat(),
                    "chunk_count": chunk_count,
                    "status": "completed",
                }
            )
        except Exception as e:
            print(f"Error marking as processed: {e}")

    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            documents_collection = self.client.collections.get(
                self.config.COLLECTION_DOCUMENTS
            )
            
            response = documents_collection.query.fetch_objects(
                filters=Filter.by_property("document_id").equal(document_id),
                limit=1
            )
            
            if response.objects and len(response.objects) > 0:
                return response.objects[0].properties
            return None
        except Exception as e:
            print(f"Error getting document metadata: {e}")
            return None
    
    def get_batch_document_metadata(self, document_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        try:
            documents_collection = self.client.collections.get(
                self.config.COLLECTION_DOCUMENTS
            )
            
            metadata_map = {}
            
            for doc_id in document_ids:
                response = documents_collection.query.fetch_objects(
                    filters=Filter.by_property("document_id").equal(doc_id),
                    limit=10
                )
                if response.objects and len(response.objects) > 0:
                    # If multiple results, prefer the one with URL, otherwise take first
                    best_obj = None
                    for obj in response.objects:
                        if obj.properties.get("url"):
                            best_obj = obj
                            break
                    if not best_obj:
                        best_obj = response.objects[0]
                    metadata_map[doc_id] = best_obj.properties
            
            return metadata_map
        except Exception as e:
            print(f"Error getting batch document metadata: {e}")
            return {}
    
    def get_processing_stats(self) -> Dict[str, Any]:
        try:
            documents_collection = self.client.collections.get(
                self.config.COLLECTION_DOCUMENTS
            )
            chunks_collection = self.client.collections.get(
                self.config.COLLECTION_CHUNKS
            )
            history_collection = self.client.collections.get(
                self.config.COLLECTION_HISTORY
            )

            docs_agg = documents_collection.aggregate.over_all(total_count=True)
            chunks_agg = chunks_collection.aggregate.over_all(total_count=True)
            history_agg = history_collection.aggregate.over_all(total_count=True)

            level_counts = {}
            for level in ChunkLevel:
                level_response = chunks_collection.aggregate.over_all(
                    filters=Filter.by_property("level").equal(level.name),
                    total_count=True,
                )
                level_counts[level.name] = level_response.total_count or 0

            return {
                "total_documents": docs_agg.total_count or 0,
                "total_chunks": chunks_agg.total_count or 0,
                "total_documents_processed": history_agg.total_count or 0,
                "chunks_by_level": level_counts,
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def _chunk_to_weaviate_object(self, chunk: BaseChunk) -> Dict[str, Any]:
        obj = {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "level": chunk.level.name,
            "content": chunk.content,
            "section_name": "",
            "subsection_name": "",
            "paragraph_index": 0,
            "is_statistical": False,
            "parent_chunk_id": "",
            "subsection_count": 0,
            "has_statistical_data": False,
        }

        if hasattr(chunk, "section_name") and isinstance(chunk.section_name, str):
            obj["section_name"] = chunk.section_name
        if hasattr(chunk, "subsection_name"):
            obj["subsection_name"] = chunk.subsection_name or ""
        if hasattr(chunk, "parent_chunk_id") and isinstance(chunk.parent_chunk_id, str):
            obj["parent_chunk_id"] = chunk.parent_chunk_id
        if hasattr(chunk, "parent_section_id") and isinstance(
            chunk.parent_section_id, str
        ):
            obj["parent_chunk_id"] = chunk.parent_section_id
        if hasattr(chunk, "paragraph_index") and isinstance(chunk.paragraph_index, int):
            obj["paragraph_index"] = chunk.paragraph_index
        if hasattr(chunk, "is_statistical") and isinstance(chunk.is_statistical, bool):
            obj["is_statistical"] = chunk.is_statistical
        if hasattr(chunk, "subsection_count") and isinstance(
            chunk.subsection_count, int
        ):
            obj["subsection_count"] = chunk.subsection_count
        if hasattr(chunk, "has_statistical_data") and isinstance(
            chunk.has_statistical_data, bool
        ):
            obj["has_statistical_data"] = chunk.has_statistical_data

        return obj

    def clear_all_collections(self):
        """
        Clear all objects from chunks, documents, and history collections.
        This will delete all indexed data.
        """
        try:
            print("Clearing vector store collections...")
            
            # Clear chunks collection
            try:
                chunks_collection = self.client.collections.get(
                    self.config.COLLECTION_CHUNKS
                )
                result = chunks_collection.data.delete_many()
                print(f"  ✓ Deleted {result.successful} objects from {self.config.COLLECTION_CHUNKS}")
            except Exception as e:
                print(f"  ✗ Error clearing chunks collection: {e}")
            
            # Clear documents collection
            try:
                documents_collection = self.client.collections.get(
                    self.config.COLLECTION_DOCUMENTS
                )
                result = documents_collection.data.delete_many()
                print(f"  ✓ Deleted {result.successful} objects from {self.config.COLLECTION_DOCUMENTS}")
            except Exception as e:
                print(f"  ✗ Error clearing documents collection: {e}")
            
            # Clear history collection
            try:
                history_collection = self.client.collections.get(
                    self.config.COLLECTION_HISTORY
                )
                result = history_collection.data.delete_many()
                print(f"  ✓ Deleted {result.successful} objects from {self.config.COLLECTION_HISTORY}")
            except Exception as e:
                print(f"  ✗ Error clearing history collection: {e}")
            
            print("✓ Vector store cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            return False

    def close(self):
        if self.client:
            self.client.close()
