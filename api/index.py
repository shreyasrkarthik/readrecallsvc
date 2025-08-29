"""
Vercel serverless function entry point for ReadRecall FastAPI service
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

# Core imports
from core.config import settings
from core.database import create_tables
from utils.schemas import HealthResponse

# API routes
from api.auth import router as auth_router
from api.books import router as books_router
from api.summaries import router as summaries_router
from api.characters import router as characters_router
from api.reading_state import router as reading_state_router

# Services
from services.opensearch_service import opensearch_service
from services.gemini_service import gemini_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router, prefix="/api")
app.include_router(books_router, prefix="/api")
app.include_router(summaries_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(reading_state_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting ReadRecall FastAPI service on Vercel...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    # Test OpenSearch connection
    try:
        if opensearch_service.health_check():
            logger.info("OpenSearch connection verified")
        else:
            logger.warning("OpenSearch health check failed")
    except Exception as e:
        logger.error(f"OpenSearch initialization error: {e}")
    
    # Test Gemini connection
    try:
        if gemini_service.test_connection():
            logger.info("Gemini API connection verified")
        else:
            logger.warning("Gemini API connection test failed")
    except Exception as e:
        logger.error(f"Gemini API initialization error: {e}")
    
    logger.info("ReadRecall FastAPI service started successfully on Vercel")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down ReadRecall FastAPI service...")


# Root endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="ReadRecall API Service",
        version=settings.version,
        environment=settings.environment
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="ReadRecall API Service",
        version=settings.version,
        environment=settings.environment
    )


# Export the app for Vercel
app.debug = settings.environment == "development"
