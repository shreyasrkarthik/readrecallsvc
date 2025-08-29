"""
Configuration settings for the ReadRecall FastAPI service
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    app_name: str = "ReadRecall API Service"
    version: str = "1.0.0"
    description: str = "FastAPI service for ReadRecall book processing and summarization"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # Database Configuration
    database_url: str
    
    # Security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 48
    
    # OpenSearch Configuration
    opensearch_host: str
    opensearch_user: Optional[str] = None
    opensearch_password: Optional[str] = None
    opensearch_index_books: str = "books"
    opensearch_index_summaries: str = "summaries"
    opensearch_index_characters: str = "characters"
    
    # AI Service Configuration
    gemini_api_key: Optional[str] = None
    
    # File Upload Configuration
    upload_folder: str = "uploads"
    max_content_length: int = 104857600  # 100MB
    allowed_extensions: List[str] = [".pdf", ".epub"]
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Logging
    log_level: str = "INFO"
    
    # Processing Configuration
    summary_percentage_step: int = 5
    
    @property
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string"""
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == 'cors_origins':
                return [x.strip() for x in raw_val.split(',')]
            return cls.json_loads(raw_val)


# Global settings instance
settings = Settings()
