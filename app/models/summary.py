"""
Summary model
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    book_id = Column(String(36), ForeignKey("books.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)  # For user-specific summaries
    progress = Column(Integer, nullable=False, index=True)  # Percentage progress (0-100)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="summaries")
    
    def to_dict(self):
        return {
            "id": self.id,
            "bookId": self.book_id,
            "userId": self.user_id,
            "progress": self.progress,
            "content": self.content,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
