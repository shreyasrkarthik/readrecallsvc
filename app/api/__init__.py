"""
API module for ReadRecall FastAPI service
"""

from .deps import get_current_user, get_db
from .auth import router as auth_router
from .books import router as books_router
from .summaries import router as summaries_router
from .characters import router as characters_router
from .reading_state import router as reading_state_router

__all__ = [
    "get_current_user",
    "get_db",
    "auth_router",
    "books_router", 
    "summaries_router",
    "characters_router",
    "reading_state_router",
]
