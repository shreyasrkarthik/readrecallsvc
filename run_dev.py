#!/usr/bin/env python3
"""
Development server runner for ReadRecall FastAPI service
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Set development environment
    os.environ.setdefault("ENVIRONMENT", "development")
    
    # Run the development server
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True
    )
