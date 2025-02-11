"""
@fileoverview
This is the main entry point for the File Concatenator application. It sets up
the FastAPI application, configures middleware, mounts static files, and includes
API routes. It also handles environment variable loading and logging configuration.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logging_config import setup_logging
from app.api.routes import router
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="File Concatenator",
    description="A service to concatenate files from GitHub repositories",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(router, prefix="")

# Create required directories
Path("output").mkdir(exist_ok=True)
Path("cache").mkdir(exist_ok=True)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup actions
    logger.info("Starting File Concatenator service")
    logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    logger.info(f"GitHub token configured: {'Yes' if os.getenv('GITHUB_TOKEN') else 'No'}")
    logger.info(f"Stripe configuration: {'Yes' if os.getenv('STRIPE_SECRET_KEY') else 'No'}")
    logger.info(f"Cache directory: {os.getenv('CACHE_DIR', 'cache')}")
    logger.info(f"Cache TTL: {os.getenv('CACHE_TTL', '3600')} seconds")
    
    yield  # This is where the application runs

    # Shutdown actions (if any)
    logger.info("Shutting down File Concatenator service")

# Assign the lifespan context manager to the app
app.lifespan = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
