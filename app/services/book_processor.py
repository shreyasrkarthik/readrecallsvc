"""
Book processing service for handling file uploads and content extraction
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import PyPDF2
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from ..core.config import settings

logger = logging.getLogger(__name__)


class BookProcessor:
    def __init__(self):
        """Initialize book processor"""
        self.upload_folder = Path(settings.upload_folder)
        self.upload_folder.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text content from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                chapters = []
                full_text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    full_text += page_text
                    
                    # Create a chapter for each page (simplified approach)
                    chapters.append({
                        "title": f"Page {page_num + 1}",
                        "content": [
                            {
                                "type": "paragraph",
                                "text": page_text
                            }
                        ]
                    })
                
                return {
                    "title": os.path.basename(file_path).replace('.pdf', ''),
                    "author": "Unknown",
                    "chapters": chapters,
                    "full_text": full_text
                }
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    def extract_text_from_epub(self, file_path: str) -> Dict[str, Any]:
        """Extract text content from EPUB file"""
        try:
            book = epub.read_epub(file_path)
            
            title = "Unknown"
            author = "Unknown"
            
            # Extract metadata
            if book.get_metadata('DC', 'title'):
                title = book.get_metadata('DC', 'title')[0][0]
            if book.get_metadata('DC', 'creator'):
                author = book.get_metadata('DC', 'creator')[0][0]
            
            chapters = []
            full_text = ""
            
            # Extract content from each chapter
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    
                    # Extract text from paragraphs
                    paragraphs = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    chapter_content = []
                    chapter_text = ""
                    
                    for para in paragraphs:
                        text = para.get_text().strip()
                        if text:
                            chapter_content.append({
                                "type": "paragraph",
                                "text": text
                            })
                            chapter_text += text + " "
                    
                    if chapter_content:
                        chapters.append({
                            "title": item.get_name() or f"Chapter {len(chapters) + 1}",
                            "content": chapter_content
                        })
                        full_text += chapter_text
            
            return {
                "title": title,
                "author": author,
                "chapters": chapters,
                "full_text": full_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from EPUB {file_path}: {e}")
            raise
    
    def process_book_file(self, file_path: str) -> Dict[str, Any]:
        """Process a book file and extract content"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.epub':
            return self.extract_text_from_epub(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def flatten_paragraphs(self, book_json: Dict[str, Any]) -> List[str]:
        """Extract all paragraphs from book JSON in reading order"""
        paragraphs = []
        
        for chapter in book_json.get("chapters", []):
            for block in chapter.get("content", []):
                if block.get("type") == "paragraph":
                    paragraphs.append(block["text"].strip())
        
        logger.info(f"Flattened book into {len(paragraphs)} paragraphs")
        return paragraphs
    
    def create_book_sections(self, book_json: Dict[str, Any], book_id: str) -> List[Dict[str, Any]]:
        """Create book sections from processed book content"""
        sections = []
        current_position = 0
        
        for idx, chapter in enumerate(book_json.get("chapters", [])):
            chapter_text = ""
            for block in chapter.get("content", []):
                if block.get("type") == "paragraph":
                    chapter_text += block["text"] + "\n\n"
            
            start_position = current_position
            end_position = current_position + len(chapter_text)
            
            sections.append({
                "book_id": book_id,
                "title": chapter.get("title", f"Chapter {idx + 1}"),
                "content": chapter_text.strip(),
                "order_index": idx,
                "start_position": start_position,
                "end_position": end_position
            })
            
            current_position = end_position
        
        logger.info(f"Created {len(sections)} book sections")
        return sections
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if the file is a supported book format"""
        if not os.path.exists(file_path):
            return False
        
        file_extension = Path(file_path).suffix.lower()
        return file_extension in settings.allowed_extensions
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information"""
        file_path = Path(file_path)
        
        return {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix.lower(),
            "modified_time": file_path.stat().st_mtime
        }


# Global book processor instance
book_processor = BookProcessor()
