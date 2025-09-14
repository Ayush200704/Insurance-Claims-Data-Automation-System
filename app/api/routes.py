"""
API Routes for Insurance Claims Data Automation System
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List, Optional
import pandas as pd
import os
from loguru import logger

from app.core.database import get_claims_data, get_db
from app.services.data_pipeline import DataPipelineService
from app.services.reserve_calculator import ReserveCalculatorService
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/data/summary")
async def get_data_summary():
    """Get summary statistics of the insurance claims data"""
    try:
        df = get_claims_data()
        
        summary = {
            "total_records": int(len(df)),
            "claim_rate": float(df['insuranceclaim'].mean()),
            "average_age": float(df['age'].mean()),
            "average_bmi": float(df['bmi'].mean()),
            "average_charges": float(df['charges'].mean()),
            "smoker_rate": float(df['smoker'].mean()),
            "sex_distribution": {
                "female": int((df['sex'] == 0).sum()),
                "male": int((df['sex'] == 1).sum())
            },
            "region_distribution": {int(k): int(v) for k, v in df['region'].value_counts().to_dict().items()},
            "children_distribution": {int(k): int(v) for k, v in df['children'].value_counts().to_dict().items()}
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/process")
async def process_data_pipeline(request: Request):
    """Process the data pipeline"""
    try:
        pipeline_service = request.app.state.data_pipeline
        df = get_claims_data()
        
        # Clean and transform data
        df_clean = pipeline_service.clean_data(df)
        df_transformed = pipeline_service.transform_data(df_clean)
        
        # Train model
        model_results = pipeline_service.train_model(df_transformed)
        
        return {
            "message": "Data pipeline processed successfully",
            "records_processed": len(df_transformed),
            "model_performance": model_results
        }
        
    except Exception as e:
        logger.error(f"Error processing data pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reserves/calculate")
async def calculate_reserves(request: Request, method: str = "chain_ladder"):
    """Calculate insurance reserves using specified method"""
    try:
        reserve_service = request.app.state.reserve_calculator
        df = get_claims_data()
        
        if method == "chain_ladder":
            results = reserve_service.calculate_chain_ladder_reserves(df)
        elif method == "bornhuetter_ferguson":
            results = reserve_service.calculate_bornhuetter_ferguson_reserves(df)
        elif method == "frequency_severity":
            results = reserve_service.calculate_frequency_severity_reserves(df)
        else:
            raise HTTPException(status_code=400, detail="Invalid method specified")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating reserves: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reserves/summary")
async def get_reserve_summary(request: Request):
    """Get summary of reserve calculations"""
    try:
        reserve_service = request.app.state.reserve_calculator
        summary = reserve_service.get_reserve_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error getting reserve summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends/analyze")
async def analyze_trends(request: Request):
    """Perform trend analysis on claims data"""
    try:
        reserve_service = request.app.state.reserve_calculator
        df = get_claims_data()
        
        trends = reserve_service.perform_trend_analysis(df)
        return trends
        
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/excel")
async def generate_excel_dashboard(request: Request):
    """Generate Excel dashboard with current data"""
    try:
        # Get dashboard service from app state
        dashboard_service = getattr(request.app.state, 'dashboard_service', None)
        if not dashboard_service:
            # Create service if not available
            dashboard_service = DashboardService()
        
        df = get_claims_data()
        
        # Generate Excel dashboard
        file_path = dashboard_service.generate_excel_dashboard(df)
        
        # Return just the filename for download
        filename = os.path.basename(file_path)
        
        return {
            "message": "Excel dashboard generated successfully",
            "file_path": file_path,
            "filename": filename,
            "download_url": f"/reports/{filename}"
        }
        
    except Exception as e:
        logger.error(f"Error generating Excel dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/download/{filename}")
async def download_excel_dashboard(filename: str):
    """Download Excel dashboard file"""
    try:
        file_path = os.path.join("reports", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        logger.error(f"Error downloading Excel dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/data")
async def get_dashboard_data():
    """Get data for dashboard visualization"""
    try:
        df = get_claims_data()
        
        # Prepare data for dashboard
        dashboard_data = {
            "claims_by_age": {int(k): float(v) for k, v in df.groupby('age')['insuranceclaim'].mean().to_dict().items()},
            "claims_by_bmi": {str(k): float(v) for k, v in df.groupby(pd.cut(df['bmi'], bins=10))['insuranceclaim'].mean().to_dict().items()},
            "claims_by_region": {int(k): float(v) for k, v in df.groupby('region')['insuranceclaim'].mean().to_dict().items()},
            "charges_distribution": {k: float(v) for k, v in df['charges'].describe().to_dict().items()},
            "smoker_impact": {int(k): float(v) for k, v in df.groupby('smoker')['insuranceclaim'].mean().to_dict().items()},
            "sex_impact": {int(k): float(v) for k, v in df.groupby('sex')['insuranceclaim'].mean().to_dict().items()}
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{record_id}")
async def predict_claim(record_id: int):
    """Predict insurance claim for a specific record"""
    try:
        df = get_claims_data()
        
        if record_id >= len(df) or record_id < 0:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Get the specific record
        record = df.iloc[record_id]
        
        # Simple prediction logic (in real implementation, use trained model)
        prediction_score = (
            record['age'] * 0.01 +
            record['bmi'] * 0.02 +
            record['smoker'] * 0.3 +
            record['children'] * 0.05
        )
        
        prediction = 1 if prediction_score > 0.5 else 0
        
        return {
            "record_id": record_id,
            "prediction": prediction,
            "confidence": min(prediction_score, 1.0),
            "actual": record['insuranceclaim']
        }
        
    except Exception as e:
        logger.error(f"Error predicting claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))
