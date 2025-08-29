"""
Characters API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.user import User
from ..models.book import Book
from ..models.character import Character
from ..utils.schemas import CharacterResponse
from ..services.opensearch_service import opensearch_service
from ..services.gemini_service import gemini_service
from ..services.book_processor import book_processor
from .deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/{book_id}", response_model=List[CharacterResponse])
def get_characters(
    book_id: str,
    percentage: int = Query(100, ge=0, le=100, description="Reading progress percentage"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get characters for a book based on reading progress (AWS Lambda equivalent)"""
    try:
        # Check access
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
        
        # Get characters that have appeared by this progress point
        characters = db.query(Character).filter(
            Character.book_id == book_id,
            Character.progress <= percentage
        ).order_by(Character.progress.desc()).all()
        
        return [CharacterResponse.model_validate(character) for character in characters]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get characters error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{book_id}/generate")
def generate_characters(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate character list for a book (AWS Lambda equivalent)"""
    try:
        # Check access
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
        
        # Check if book has been processed
        if not book.epub_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book file not available for processing"
            )
        
        # Extract book content
        book_data = book_processor.process_book_file(book.epub_url)
        full_text = book_data.get("full_text", "")
        
        if not full_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content found in book"
            )
        
        # Generate character lists using Gemini
        characters_data = gemini_service.generate_percentage_characters(
            full_text, book_id, current_user.id
        )
        
        # Save characters to database
        created_count = 0
        for character_data in characters_data:
            # Check if character list already exists for this progress
            existing = db.query(Character).filter_by(
                book_id=book_id,
                progress=character_data["progress"]
            ).first()
            
            if not existing:
                character = Character(**character_data)
                db.add(character)
                created_count += 1
                
                # Index in OpenSearch
                opensearch_service.index_character(character_data)
        
        db.commit()
        
        logger.info(f"Generated {created_count} character lists for book {book_id}")
        return {
            "message": "Characters generated successfully",
            "charactersCreated": created_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate characters error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during character generation"
        )


@router.get("/{book_id}/search", response_model=List[CharacterResponse])
def search_characters(
    book_id: str,
    q: str = Query(..., description="Search query"),
    max_progress: int = Query(100, ge=0, le=100, description="Maximum progress to search"),
    size: int = Query(10, ge=1, le=50, description="Number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search characters for a book"""
    try:
        # Check access
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
        
        # Search using OpenSearch
        search_results = opensearch_service.search_characters(
            book_id, q, max_progress, size
        )
        
        # Convert to response models
        characters = []
        for result in search_results:
            characters.append(CharacterResponse(**result))
        
        return characters
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search characters error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search"
        )
