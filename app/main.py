"""
Main FastAPI application for ReadRecall service
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import uvicorn

# Core imports
from .core.config import settings
from .core.database import create_tables
from .utils.schemas import HealthResponse

# API routes
from .api.auth import router as auth_router
from .api.books import router as books_router
from .api.summaries import router as summaries_router
from .api.characters import router as characters_router
from .api.reading_state import router as reading_state_router

# Services
from .services.opensearch_service import opensearch_service
from .services.gemini_service import gemini_service

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
    logger.info("Starting ReadRecall FastAPI service...")
    
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
    
    logger.info("ReadRecall FastAPI service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down ReadRecall FastAPI service...")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ReadRecall FastAPI Service",
        "version": settings.version,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.version
    )


# Test Gemini endpoint
@app.get("/test-gemini", response_model=HealthResponse)
async def test_gemini():
    """Test Gemini API connection"""
    try:
        is_working = gemini_service.test_connection()
        
        if is_working:
            return HealthResponse(
                status="success",
                timestamp=datetime.utcnow().isoformat(),
                message="Gemini API is working correctly"
            )
        else:
            return HealthResponse(
                status="error",
                timestamp=datetime.utcnow().isoformat(),
                message="Gemini API test failed"
            )
            
    except Exception as e:
        logger.error(f"Gemini test error: {e}")
        return HealthResponse(
            status="error",
            timestamp=datetime.utcnow().isoformat(),
            message=f"Gemini API error: {str(e)}"
        )


# Test OpenSearch endpoint
@app.get("/test-opensearch", response_model=HealthResponse)
async def test_opensearch():
    """Test OpenSearch connection"""
    try:
        is_healthy = opensearch_service.health_check()
        
        if is_healthy:
            return HealthResponse(
                status="success",
                timestamp=datetime.utcnow().isoformat(),
                message="OpenSearch is healthy"
            )
        else:
            return HealthResponse(
                status="error",
                timestamp=datetime.utcnow().isoformat(),
                message="OpenSearch health check failed"
            )
            
    except Exception as e:
        logger.error(f"OpenSearch test error: {e}")
        return HealthResponse(
            status="error",
            timestamp=datetime.utcnow().isoformat(),
            message=f"OpenSearch error: {str(e)}"
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# 404 handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404 Not Found handler"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Endpoint not found"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
