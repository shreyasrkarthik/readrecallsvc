"""
Gemini AI service for generating summaries and character lists
"""

import google.generativeai as genai
import time
import logging
from typing import List, Dict, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        """Initialize Gemini AI service"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.max_retries = 5
        self.base_wait_time = 2
    
    def _call_gemini_with_retry(self, prompt: str, text: str) -> str:
        """Call Gemini API with retry logic for rate limiting"""
        full_prompt = f"{prompt}\n\n{text}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling Gemini API (Attempt {attempt + 1}/{self.max_retries})...")
                
                response = self.model.generate_content(full_prompt)
                
                if response.text:
                    logger.info("Gemini API call successful.")
                    return response.text.strip()
                else:
                    logger.warning("Gemini API returned empty response")
                    return ""
                    
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = self.base_wait_time * (2 ** attempt)
                    logger.warning(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Gemini API error: {e}")
                    raise
        
        logger.error(f"Failed to call Gemini API after {self.max_retries} retries")
        raise RuntimeError(f"Gemini API rate limit exceeded after {self.max_retries} retries")
    
    def generate_summary(self, text: str) -> str:
        """Generate a summary for the given text"""
        prompt = (
            "Provide a concise recap under 250-300 words of the following book content. "
            "Focus on key events and characters. Write in a clear, engaging style that helps "
            "readers recall what they've read so far."
        )
        
        try:
            return self._call_gemini_with_retry(prompt, text)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Fallback: return truncated text
            return text[:400] + " …[truncated]" if len(text) > 400 else text
    
    def generate_character_list(self, text: str) -> str:
        """Generate a character list for the given text"""
        prompt = (
            "Provide a concise list of all the characters that appear in the following book content, "
            "similar to the X-ray feature of Prime Video. For each character, include a one-line "
            "description of who they are and their role. Format as a clean list. "
            "Only return the character list, nothing else."
        )
        
        try:
            return self._call_gemini_with_retry(prompt, text)
        except Exception as e:
            logger.error(f"Failed to generate character list: {e}")
            # Fallback: return truncated text
            return text[:400] + " …[truncated]" if len(text) > 400 else text
    
    def generate_percentage_summaries(self, book_content: str, book_id: str, user_id: str) -> List[Dict]:
        """Generate summaries at percentage intervals"""
        logger.info(f"Generating percentage summaries for book {book_id}")
        
        if not book_content:
            logger.warning("No book content provided for summarization")
            return []
        
        total_length = len(book_content)
        summaries_to_save = []
        last_end = -1
        
        # Generate summaries at percentage intervals
        for percentage in range(settings.summary_percentage_step, 101, settings.summary_percentage_step):
            end_idx = int(total_length * percentage / 100)
            
            # Ensure we process a new slice of text
            if end_idx == last_end:
                continue
            
            slice_text = book_content[:end_idx]
            logger.info(f"Processing up to {percentage}% ({len(slice_text)} characters) for summary")
            
            # Generate summary for this slice
            summary_content = self.generate_summary(slice_text)
            
            summaries_to_save.append({
                "book_id": book_id,
                "user_id": user_id,
                "progress": percentage,
                "content": summary_content,
            })
            
            last_end = end_idx
        
        logger.info(f"Generated {len(summaries_to_save)} summaries")
        return summaries_to_save
    
    def generate_percentage_characters(self, book_content: str, book_id: str, user_id: str) -> List[Dict]:
        """Generate character lists at percentage intervals"""
        logger.info(f"Generating percentage characters for book {book_id}")
        
        if not book_content:
            logger.warning("No book content provided for character extraction")
            return []
        
        total_length = len(book_content)
        characters_to_save = []
        last_end = -1
        
        # Generate character lists at percentage intervals
        for percentage in range(settings.summary_percentage_step, 101, settings.summary_percentage_step):
            end_idx = int(total_length * percentage / 100)
            
            # Ensure we process a new slice of text
            if end_idx == last_end:
                continue
            
            slice_text = book_content[:end_idx]
            logger.info(f"Processing up to {percentage}% ({len(slice_text)} characters) for characters")
            
            # Generate character list for this slice
            characters_content = self.generate_character_list(slice_text)
            
            characters_to_save.append({
                "book_id": book_id,
                "user_id": user_id,
                "progress": percentage,
                "name": f"Characters at {percentage}%",
                "description": f"Character list up to {percentage}% of the book",
                "characters_list": characters_content,
            })
            
            last_end = end_idx
        
        logger.info(f"Generated {len(characters_to_save)} character lists")
        return characters_to_save
    
    def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            test_prompt = "Say 'Hello, this is a test' and nothing else."
            response = self.model.generate_content(test_prompt)
            return bool(response.text and "hello" in response.text.lower())
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False


# Global Gemini service instance
gemini_service = GeminiService()
