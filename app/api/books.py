"""
Books API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.user import User
from ..models.book import Book, BookSection
from ..models.reading_state import ReadingState
from ..utils.schemas import BookResponse, BookUpload, UploadResponse
from ..services.opensearch_service import opensearch_service
from ..services.book_processor import book_processor
from ..services.file_manager import file_manager
from ..services.gemini_service import gemini_service
from .deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[BookResponse])
def get_user_books(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all books for the current user"""
    try:
        # Get books uploaded by user or public domain books
        books = db.query(Book).filter(
            (Book.uploaded_by_id == current_user.id) | (Book.is_public_domain == True)
        ).all()
        
        books_data = []
        for book in books:
            # Get reading state for this user
            reading_state = db.query(ReadingState).filter_by(
                user_id=current_user.id,
                book_id=book.id
            ).first()
            
            book_dict = book.to_dict()
            book_dict["readingState"] = reading_state.to_dict() if reading_state else {
                "position": 0,
                "currentReadingPercentage": 0,
                "updatedAt": None
            }
            
            books_data.append(BookResponse(**book_dict))
        
        return books_data
        
    except Exception as e:
        logger.error(f"Get books error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific book by ID"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Check if user has access to this book
        if not book.is_public_domain and book.uploaded_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get reading state
        reading_state = db.query(ReadingState).filter_by(
            user_id=current_user.id,
            book_id=book.id
        ).first()
        
        # Get sections
        sections = db.query(BookSection).filter_by(
            book_id=book.id
        ).order_by(BookSection.order_index).all()
        
        book_dict = book.to_dict(include_sections=True)
        book_dict["readingState"] = reading_state.to_dict() if reading_state else {
            "position": 0,
            "currentReadingPercentage": 0,
            "updatedAt": None
        }
        
        return BookResponse(**book_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get book error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/upload", response_model=UploadResponse)
def upload_book(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new book file"""
    try:
        # Validate file type
        if not file_manager.is_valid_book_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only EPUB and PDF files are allowed"
            )
        
        # Read file content
        file_content = file.file.read()
        
        # Save file
        file_info = file_manager.save_uploaded_file(
            file_content, 
            file.filename, 
            current_user.id
        )
        
        # Create book record
        book = Book(
            title=file.filename.rsplit('.', 1)[0],  # Remove extension
            author="Unknown",  # Will be updated during processing
            file_name=file.filename,
            epub_url=file_info["file_path"],
            uploaded_by_id=current_user.id,
            is_public_domain=False,
            processing_status="UPLOADED"
        )
        
        db.add(book)
        db.commit()
        db.refresh(book)
        
        # Create initial reading state
        reading_state = ReadingState(
            user_id=current_user.id,
            book_id=book.id,
            position=0,
            current_reading_percentage=0
        )
        db.add(reading_state)
        db.commit()
        
        # Index book in OpenSearch
        opensearch_service.index_book(book.to_dict())
        
        logger.info(f"Book uploaded successfully: {book.id}")
        return UploadResponse(
            upload_path=file_info["file_path"],
            book_id=book.id,
            message="Book uploaded successfully. Processing will begin shortly."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during upload"
        )


@router.post("/{book_id}/process")
def process_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process an uploaded book (extract metadata, sections, etc.)"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Check ownership
        if book.uploaded_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if not book.epub_url or not file_manager.get_file_info(book.epub_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book file not found"
            )
        
        # Process the book file
        book_data = book_processor.process_book_file(book.epub_url)
        
        # Update book metadata
        book.title = book_data.get("title", book.title)
        book.author = book_data.get("author", book.author)
        book.processing_status = "PROCESSED"
        
        # Create book sections
        sections_data = book_processor.create_book_sections(book_data, book.id)
        
        # Save sections to database
        for section_data in sections_data:
            section = BookSection(**section_data)
            db.add(section)
        
        db.commit()
        
        # Update book in OpenSearch
        opensearch_service.index_book(book.to_dict())
        
        logger.info(f"Book processed successfully: {book.id}")
        return {
            "message": "Book processed successfully",
            "sectionsCreated": len(sections_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process book error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during processing"
        )


@router.post("/generate-upload-url", response_model=UploadResponse)
def generate_upload_url(
    upload_data: BookUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate upload information for a book (AWS Lambda equivalent)"""
    try:
        # Validate file extension
        if not file_manager.is_valid_book_file(upload_data.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file extension"
            )
        
        # Generate upload info
        upload_info = file_manager.generate_presigned_upload_info(
            upload_data.filename,
            current_user.id
        )
        
        # Create book record
        book = Book(
            id=upload_info["book_id"],
            title=upload_data.filename.rsplit('.', 1)[0],
            author="Unknown",
            file_name=upload_data.filename,
            epub_url=upload_info["upload_path"],  # Set the epub_url to the upload path
            uploaded_by_id=current_user.id,
            is_public_domain=False,
            processing_status="UPLOAD_PENDING"
        )
        
        db.add(book)
        db.commit()
        
        # Create initial reading state
        reading_state = ReadingState(
            user_id=current_user.id,
            book_id=book.id,
            position=0,
            current_reading_percentage=0
        )
        db.add(reading_state)
        db.commit()
        
        logger.info(f"Upload URL generated for book: {book.id}")
        return UploadResponse(
            upload_path=upload_info["upload_path"],
            book_id=upload_info["book_id"],
            message="Pre-signed URL generated and book entry created."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate upload URL error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
