"""
Insurance Claims Data Automation System - Main Application
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger
import pandas as pd
import os

from app.core.config import settings
from app.api.routes import router
from app.core.database import init_db
from app.services.data_pipeline import DataPipelineService
from app.services.reserve_calculator import ReserveCalculatorService
from app.services.dashboard_service import DashboardService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Insurance Claims Data Automation System")
    await init_db()
    
    # Initialize services
    app.state.data_pipeline = DataPipelineService()
    app.state.reserve_calculator = ReserveCalculatorService()
    app.state.dashboard_service = DashboardService()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Insurance Claims Data Automation System")


app = FastAPI(
    title="Insurance Claims Data Automation System",
    description="Automated data pipeline for insurance claims processing, reserve calculation, and reporting",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")


@app.get("/")
async def root():
    """Root endpoint - serve the frontend"""
    return FileResponse('static/index.html')


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "insurance-claims-automation"}


@app.post("/upload-data")
async def upload_insurance_data(file: UploadFile = File(...)):
    """Upload and process insurance claims data"""
    try:
        # Save uploaded file
        file_path = f"data/{file.filename}"
        os.makedirs("data", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the data
        pipeline_service = app.state.data_pipeline
        results = pipeline_service.process_pipeline(file_path)
        
        return {
            "message": "Data uploaded and processed successfully",
            "filename": file.filename,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )