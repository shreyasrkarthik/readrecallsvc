"""
ReadingState model
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class ReadingState(Base):
    __tablename__ = "reading_states"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    book_id = Column(String(36), ForeignKey("books.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)  # Reading position/progress
    current_reading_percentage = Column(Integer, default=0)  # Current reading percentage
    total_locations = Column(Integer, nullable=True)  # Total locations in book
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to ensure one reading state per user per book
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="unique_user_book_reading_state"),)
    
    # Relationships
    user = relationship("User", back_populates="reading_states")
    book = relationship("Book", back_populates="reading_states")
    
    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "bookId": self.book_id,
            "position": self.position,
            "currentReadingPercentage": self.current_reading_percentage,
            "totalLocations": self.total_locations,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
