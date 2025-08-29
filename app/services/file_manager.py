"""
File management service for handling uploads and storage
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from werkzeug.utils import secure_filename
from ..core.config import settings

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self):
        """Initialize file manager"""
        self.upload_folder = Path(settings.upload_folder)
        self.upload_folder.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_folder / "books").mkdir(exist_ok=True)
        (self.upload_folder / "covers").mkdir(exist_ok=True)
        (self.upload_folder / "temp").mkdir(exist_ok=True)
    
    def is_valid_book_file(self, filename: str) -> bool:
        """Check if the file has a valid book extension"""
        if not filename:
            return False
        
        file_extension = Path(filename).suffix.lower()
        return file_extension in settings.allowed_extensions
    
    def generate_unique_filename(self, original_filename: str, user_id: str) -> str:
        """Generate a unique filename for uploaded files"""
        # Secure the filename
        filename = secure_filename(original_filename)
        
        # Generate unique identifier
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        
        # Create filename with user_id and unique identifier
        return f"{user_id}_{file_id}{file_extension}"
    
    def save_uploaded_file(self, file_content: bytes, filename: str, user_id: str) -> Dict[str, str]:
        """Save uploaded file to disk"""
        try:
            # Generate unique filename
            unique_filename = self.generate_unique_filename(filename, user_id)
            
            # Create user directory
            user_dir = self.upload_folder / "books" / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = user_dir / unique_filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Saved file: {file_path}")
            
            return {
                "file_path": str(file_path),
                "filename": unique_filename,
                "original_filename": filename,
                "size": len(file_content)
            }
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination"""
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            shutil.move(source_path, destination_path)
            logger.info(f"Moved file from {source_path} to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            file_stat = os.stat(file_path)
            file_path_obj = Path(file_path)
            
            return {
                "name": file_path_obj.name,
                "size": file_stat.st_size,
                "extension": file_path_obj.suffix.lower(),
                "created_time": file_stat.st_ctime,
                "modified_time": file_stat.st_mtime,
                "is_file": os.path.isfile(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def create_temp_file(self, content: bytes, extension: str = ".tmp") -> str:
        """Create a temporary file with the given content"""
        try:
            temp_filename = f"{uuid.uuid4()}{extension}"
            temp_path = self.upload_folder / "temp" / temp_filename
            
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"Created temp file: {temp_path}")
            return str(temp_path)
        except Exception as e:
            logger.error(f"Error creating temp file: {e}")
            raise
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        try:
            temp_dir = self.upload_folder / "temp"
            if not temp_dir.exists():
                return 0
            
            import time
            current_time = time.time()
            cutoff_time = current_time - (older_than_hours * 3600)
            
            deleted_count = 0
            for temp_file in temp_dir.iterdir():
                if temp_file.is_file() and temp_file.stat().st_mtime < cutoff_time:
                    try:
                        temp_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete temp file {temp_file}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} temporary files")
            return deleted_count
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
            return 0
    
    def generate_presigned_upload_info(self, filename: str, user_id: str) -> Dict[str, str]:
        """Generate information for file upload (simulating presigned URL behavior)"""
        unique_filename = self.generate_unique_filename(filename, user_id)
        
        # Create user directory path
        user_dir = self.upload_folder / "books" / user_id
        file_path = user_dir / unique_filename
        
        return {
            "upload_path": str(file_path),
            "filename": unique_filename,
            "original_filename": filename,
            "user_id": user_id,
            "book_id": str(uuid.uuid4())
        }


# Global file manager instance
file_manager = FileManager()
