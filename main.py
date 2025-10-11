"""
Vision Text OCR Service - Main Entry Point

A FastAPI service that extracts text from images using OCR technology.
Provides REST endpoints for image upload and text extraction.
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import utils
import database.database as database
from api.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events for the application.
    """
    print("Starting Vision Text OCR Service...")
    os.makedirs(utils.TEMP_DIR, exist_ok=True)
    await database.connect_to_db()
    await database.create_db_table()
    print("Vision Text OCR Service is ready!")
    yield
    print("Shutting down Vision Text OCR Service...")
    await database.close_db_connection()
    print("👋 Vision Text OCR Service stopped.")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="Vision Text OCR Service",
        description="Extract text from images using OCR",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add CORS middleware for frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"], # The address of the React UI
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the API router
    app.include_router(api_router)
    
    return app

app = create_app()

if __name__ == "__main__":
    # Run with`python main.py` for development or "uvicorn main:app"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
