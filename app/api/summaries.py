"""
Summaries API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.user import User
from ..models.book import Book
from ..models.summary import Summary
from ..utils.schemas import SummaryResponse
from ..services.opensearch_service import opensearch_service
from ..services.gemini_service import gemini_service
from ..services.book_processor import book_processor
from .deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.get("/{book_id}", response_model=List[SummaryResponse])
def get_summaries(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all summaries for a book"""
    try:
        # Check if user has access to this book
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
        
        summaries = db.query(Summary).filter_by(
            book_id=book_id
        ).order_by(Summary.progress).all()
        
        return [SummaryResponse.model_validate(summary) for summary in summaries]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get summaries error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{book_id}/by-progress", response_model=SummaryResponse)
def get_summary_by_progress(
    book_id: str,
    percentage: int = Query(..., ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary based on reading progress (AWS Lambda equivalent)"""
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
        
        # Find the most recent summary at or before the current progress
        summary = db.query(Summary).filter(
            Summary.book_id == book_id,
            Summary.progress <= percentage
        ).order_by(Summary.progress.desc()).first()
        
        if not summary:
            # Return placeholder summary
            return SummaryResponse(
                id="placeholder",
                bookId=book_id,
                userId=current_user.id,
                progress=percentage,
                content="No summary available for this position yet.",
                createdAt=None
            )
        
        return SummaryResponse.model_validate(summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get summary by progress error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{book_id}/generate")
def generate_summaries(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summaries for a book (AWS Lambda equivalent)"""
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
        
        # Generate summaries using Gemini
        summaries_data = gemini_service.generate_percentage_summaries(
            full_text, book_id, current_user.id
        )
        
        # Save summaries to database
        created_count = 0
        for summary_data in summaries_data:
            # Check if summary already exists
            existing = db.query(Summary).filter_by(
                book_id=book_id,
                progress=summary_data["progress"]
            ).first()
            
            if not existing:
                summary = Summary(**summary_data)
                db.add(summary)
                created_count += 1
                
                # Index in OpenSearch
                opensearch_service.index_summary(summary_data)
        
        db.commit()
        
        logger.info(f"Generated {created_count} summaries for book {book_id}")
        return {
            "message": "Summaries generated successfully",
            "summariesCreated": created_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate summaries error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during summary generation"
        )


@router.get("/{book_id}/search", response_model=List[SummaryResponse])
def search_summaries(
    book_id: str,
    q: str = Query(..., description="Search query"),
    max_progress: int = Query(100, ge=0, le=100, description="Maximum progress to search"),
    size: int = Query(10, ge=1, le=50, description="Number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search summaries for a book"""
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
        search_results = opensearch_service.search_summaries(
            book_id, q, max_progress, size
        )
        
        # Convert to response models
        summaries = []
        for result in search_results:
            summaries.append(SummaryResponse(**result))
        
        return summaries
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search summaries error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search"
        )
