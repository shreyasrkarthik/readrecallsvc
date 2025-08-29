"""
Simple test endpoint for Vercel deployment
"""

from fastapi import FastAPI

app = FastAPI(title="ReadRecall Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello from ReadRecall on Vercel!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ReadRecall Test"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working!", "timestamp": "now"}
