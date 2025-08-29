"""
Reading State API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.database import get_db
from ..models.user import User
from ..models.book import Book
from ..models.reading_state import ReadingState
from ..utils.schemas import ReadingStateResponse, ReadingStateUpdate
from .deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reading-state", tags=["Reading State"])


@router.get("/{book_id}", response_model=ReadingStateResponse)
def get_reading_state(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reading state for a book"""
    try:
        # Check if book exists and user has access
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        if not book.is_public_domain and book.uploaded_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        reading_state = db.query(ReadingState).filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first()
        
        if not reading_state:
            # Create a default reading state
            reading_state = ReadingState(
                user_id=current_user.id,
                book_id=book_id,
                position=0,
                current_reading_percentage=0
            )
            db.add(reading_state)
            db.commit()
            db.refresh(reading_state)
        
        return ReadingStateResponse.model_validate(reading_state)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reading state error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{book_id}", response_model=ReadingStateResponse)
def update_reading_state(
    book_id: str,
    state_update: ReadingStateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reading state for a book"""
    try:
        # Check if book exists and user has access
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        if not book.is_public_domain and book.uploaded_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Find existing reading state or create new one
        reading_state = db.query(ReadingState).filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first()
        
        if reading_state:
            # Update existing reading state
            reading_state.position = state_update.position
            if state_update.currentReadingPercentage is not None:
                reading_state.current_reading_percentage = state_update.currentReadingPercentage
            if state_update.totalLocations is not None:
                reading_state.total_locations = state_update.totalLocations
            reading_state.updated_at = datetime.utcnow()
        else:
            # Create new reading state
            reading_state = ReadingState(
                user_id=current_user.id,
                book_id=book_id,
                position=state_update.position,
                current_reading_percentage=state_update.currentReadingPercentage or 0,
                total_locations=state_update.totalLocations
            )
            db.add(reading_state)
        
        db.commit()
        db.refresh(reading_state)
        
        logger.info(f"Updated reading state for user {current_user.id}, book {book_id}")
        return ReadingStateResponse.model_validate(reading_state)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update reading state error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{book_id}")
def delete_reading_state(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete reading state for a book"""
    try:
        reading_state = db.query(ReadingState).filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first()
        
        if not reading_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading state not found"
            )
        
        db.delete(reading_state)
        db.commit()
        
        logger.info(f"Deleted reading state for user {current_user.id}, book {book_id}")
        return {"message": "Reading state deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete reading state error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
