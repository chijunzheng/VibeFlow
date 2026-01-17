from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import settings
from backend.database import create_db_and_tables
from backend.api import songs, utils
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
    
    create_db_and_tables()
    logger.info("📦 Database tables created.")
    
    yield
    
    logger.info("🛑 Shutting down VibeFlow Studio Backend")

app = FastAPI(
    title="VibeFlow Studio API",
    description="Backend for VibeFlow Studio - Local Songwriting Assistant",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs.router)
app.include_router(utils.router)