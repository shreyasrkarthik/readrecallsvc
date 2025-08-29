"""
Book and BookSection models
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Book(Base):
    __tablename__ = "books"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    cover_url = Column(String(500))
    epub_url = Column(String(500))
    file_name = Column(String(255))
    s3_key = Column(String(500))
    upload_bucket_name = Column(String(100))
    processing_status = Column(String(50), default="UPLOADED")
    is_public_domain = Column(Boolean, default=False)
    uploaded_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploaded_by = relationship("User", back_populates="books", foreign_keys=[uploaded_by_id])
    sections = relationship("BookSection", back_populates="book", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="book", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="book", cascade="all, delete-orphan")
    reading_states = relationship("ReadingState", back_populates="book", cascade="all, delete-orphan")
    
    def to_dict(self, include_sections=False):
        result = {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "coverUrl": self.cover_url,
            "epubUrl": self.epub_url,
            "fileName": self.file_name,
            "s3Key": self.s3_key,
            "uploadBucketName": self.upload_bucket_name,
            "processingStatus": self.processing_status,
            "isPublicDomain": self.is_public_domain,
            "uploadedById": self.uploaded_by_id,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sections and self.sections:
            result["sections"] = [section.to_dict() for section in self.sections]
        
        return result


class BookSection(Base):
    __tablename__ = "book_sections"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    book_id = Column(String(36), ForeignKey("books.id"), nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="sections")
    
    def to_dict(self):
        return {
            "id": self.id,
            "bookId": self.book_id,
            "title": self.title,
            "content": self.content,
            "orderIndex": self.order_index,
            "startPosition": self.start_position,
            "endPosition": self.end_position,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
