"""
Vision Text OCR Service - Main Entry Point
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
    app = FastAPI(
        title="Vision Text OCR Service",
        description="Extract text from images using OCR",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    
    @app.get("/")
    def home():
        return {"message": "Welcome to the Vision Text OCR Service. Visit /docs for API details."}
        
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
