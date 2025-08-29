"""
Character model
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    book_id = Column(String(36), ForeignKey("books.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)  # For user-specific characters
    progress = Column(Integer, nullable=False, index=True)  # Percentage progress when character appears (0-100)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    characters_list = Column(Text, nullable=True)  # Full character list at this progress point
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="characters")
    
    def to_dict(self):
        return {
            "id": self.id,
            "bookId": self.book_id,
            "userId": self.user_id,
            "progress": self.progress,
            "name": self.name,
            "description": self.description,
            "charactersList": self.characters_list,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
