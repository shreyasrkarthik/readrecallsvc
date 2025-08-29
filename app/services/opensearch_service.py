"""
OpenSearch service for search and indexing functionality
"""

from opensearchpy import OpenSearch, RequestsHttpConnection
from typing import Dict, List, Any, Optional
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class OpenSearchService:
    def __init__(self):
        """Initialize OpenSearch client"""
        auth = None
        if settings.opensearch_user and settings.opensearch_password:
            auth = (settings.opensearch_user, settings.opensearch_password)
        
        # Determine if we should use SSL based on the host URL
        use_ssl = settings.opensearch_host.startswith('https://')
        
        self.client = OpenSearch(
            hosts=[settings.opensearch_host],
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=use_ssl,  # Only verify certs if using SSL
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )
        
        # Initialize indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create OpenSearch indexes if they don't exist"""
        indexes = {
            settings.opensearch_index_books: {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "author": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "uploaded_by_id": {"type": "keyword"},
                        "is_public_domain": {"type": "boolean"},
                        "processing_status": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            },
            settings.opensearch_index_summaries: {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "book_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "progress": {"type": "integer"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "created_at": {"type": "date"}
                    }
                }
            },
            settings.opensearch_index_characters: {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "book_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "progress": {"type": "integer"},
                        "name": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "characters_list": {"type": "text", "analyzer": "standard"},
                        "created_at": {"type": "date"}
                    }
                }
            }
        }
        
        for index_name, index_config in indexes.items():
            try:
                if not self.client.indices.exists(index=index_name):
                    self.client.indices.create(index=index_name, body=index_config)
                    logger.info(f"Created OpenSearch index: {index_name}")
                else:
                    logger.info(f"OpenSearch index already exists: {index_name}")
            except Exception as e:
                logger.error(f"Error creating index {index_name}: {e}")
    
    def index_book(self, book_data: Dict[str, Any]) -> bool:
        """Index a book document"""
        try:
            response = self.client.index(
                index=settings.opensearch_index_books,
                id=book_data["id"],
                body=book_data,
                refresh=True
            )
            logger.info(f"Indexed book: {book_data['id']}")
            return response["result"] in ["created", "updated"]
        except Exception as e:
            logger.error(f"Error indexing book {book_data.get('id')}: {e}")
            return False
    
    def index_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Index a summary document"""
        try:
            response = self.client.index(
                index=settings.opensearch_index_summaries,
                id=summary_data["id"],
                body=summary_data,
                refresh=True
            )
            logger.info(f"Indexed summary: {summary_data['id']}")
            return response["result"] in ["created", "updated"]
        except Exception as e:
            logger.error(f"Error indexing summary {summary_data.get('id')}: {e}")
            return False
    
    def index_character(self, character_data: Dict[str, Any]) -> bool:
        """Index a character document"""
        try:
            response = self.client.index(
                index=settings.opensearch_index_characters,
                id=character_data["id"],
                body=character_data,
                refresh=True
            )
            logger.info(f"Indexed character: {character_data['id']}")
            return response["result"] in ["created", "updated"]
        except Exception as e:
            logger.error(f"Error indexing character {character_data.get('id')}: {e}")
            return False
    
    def search_books(self, query: str, user_id: str, size: int = 10) -> List[Dict[str, Any]]:
        """Search books"""
        try:
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^2", "author^2", "content"]
                                }
                            }
                        ],
                        "should": [
                            {"term": {"uploaded_by_id": user_id}},
                            {"term": {"is_public_domain": True}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "size": size
            }
            
            response = self.client.search(
                index=settings.opensearch_index_books,
                body=search_query
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return []
    
    def search_summaries(self, book_id: str, query: str, max_progress: int = 100, size: int = 10) -> List[Dict[str, Any]]:
        """Search summaries for a specific book up to a progress point"""
        try:
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"book_id": book_id}},
                            {"range": {"progress": {"lte": max_progress}}},
                            {"match": {"content": query}}
                        ]
                    }
                },
                "sort": [{"progress": {"order": "asc"}}],
                "size": size
            }
            
            response = self.client.search(
                index=settings.opensearch_index_summaries,
                body=search_query
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Error searching summaries: {e}")
            return []
    
    def search_characters(self, book_id: str, query: str, max_progress: int = 100, size: int = 10) -> List[Dict[str, Any]]:
        """Search characters for a specific book up to a progress point"""
        try:
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"book_id": book_id}},
                            {"range": {"progress": {"lte": max_progress}}},
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["name^2", "description", "characters_list"]
                                }
                            }
                        ]
                    }
                },
                "sort": [{"progress": {"order": "asc"}}],
                "size": size
            }
            
            response = self.client.search(
                index=settings.opensearch_index_characters,
                body=search_query
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Error searching characters: {e}")
            return []
    
    def delete_book_documents(self, book_id: str) -> bool:
        """Delete all documents related to a book"""
        try:
            # Delete from all indexes
            for index in [settings.opensearch_index_books, settings.opensearch_index_summaries, settings.opensearch_index_characters]:
                delete_query = {
                    "query": {
                        "term": {"book_id" if index != settings.opensearch_index_books else "id": book_id}
                    }
                }
                
                self.client.delete_by_query(
                    index=index,
                    body=delete_query,
                    refresh=True
                )
            
            logger.info(f"Deleted all documents for book: {book_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents for book {book_id}: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if OpenSearch is healthy"""
        try:
            response = self.client.cluster.health()
            return response["status"] in ["green", "yellow"]
        except Exception as e:
            logger.error(f"OpenSearch health check failed: {e}")
            return False


# Global OpenSearch service instance
opensearch_service = OpenSearchService()
