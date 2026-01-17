from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vibeflow")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.
    Checks configuration on startup.
    """
    logger.info("🚀 Starting VibeFlow Studio Backend")
    
    if not settings.is_gemini_configured:
        logger.warning("⚠️  GEMINI_API_KEY is missing! VibeFlow features will be limited.")
    else:
        logger.info("✅ Gemini API Key loaded successfully.")
    
    yield
    
    logger.info("🛑 Shutting down VibeFlow Studio Backend")

app = FastAPI(
    title="VibeFlow Studio API",
    description="Backend for VibeFlow Studio - Local Songwriting Assistant",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to VibeFlow Studio API",
        "status": "running",
        "config": {
            "gemini_configured": settings.is_gemini_configured
        }
    }
