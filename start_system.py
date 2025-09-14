"""
Startup script for Insurance Claims Data Automation System
"""
import os
import sys
import pandas as pd
from loguru import logger
from app.core.database import init_db, load_data_to_db
from app.services.data_pipeline import DataPipelineService
from app.services.reserve_calculator import ReserveCalculatorService
from app.services.dashboard_service import DashboardService
import asyncio

async def initialize_system():
    """Initialize the insurance claims automation system"""
    logger.info("🚀 Initializing Insurance Claims Data Automation System")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized successfully")
        
        # Load sample data if available
        if os.path.exists('insurance2.csv'):
            logger.info("📁 Loading sample data...")
            records_loaded = load_data_to_db('insurance2.csv')
            logger.info(f"✅ Loaded {records_loaded} records from insurance2.csv")
        else:
            logger.warning("⚠️ Sample data file (insurance2.csv) not found")
        
        # Initialize services
        logger.info("🔧 Initializing services...")
        pipeline_service = DataPipelineService()
        reserve_service = ReserveCalculatorService()
        dashboard_service = DashboardService()
        logger.info("✅ Services initialized successfully")
        
        # Process data pipeline if data is available
        if os.path.exists('insurance2.csv'):
            logger.info("🔄 Processing data pipeline...")
            df = pd.read_csv('insurance2.csv')
            
            # Clean and transform data
            df_clean = pipeline_service.clean_data(df)
            df_transformed = pipeline_service.transform_data(df_clean)
            
            # Train model
            model_results = pipeline_service.train_model(df_transformed)
            logger.info(f"✅ Model trained with accuracy: {model_results['accuracy']:.4f}")
            
            # Calculate reserves
            logger.info("💰 Calculating reserves...")
            chain_ladder_results = reserve_service.calculate_chain_ladder_reserves(df)
            bf_results = reserve_service.calculate_bornhuetter_ferguson_reserves(df)
            fs_results = reserve_service.calculate_frequency_severity_reserves(df)
            
            logger.info(f"✅ Chain Ladder reserves: ${chain_ladder_results['total_reserves']:,.2f}")
            logger.info(f"✅ Bornhuetter-Ferguson reserves: ${bf_results['total_reserves']:,.2f}")
            logger.info(f"✅ Frequency-Severity reserves: ${fs_results['total_reserves']:,.2f}")
            
            # Generate initial dashboard
            logger.info("📊 Generating initial dashboard...")
            dashboard_path = dashboard_service.generate_excel_dashboard(df)
            logger.info(f"✅ Dashboard generated: {dashboard_path}")
        
        logger.info("🎉 System initialization completed successfully!")
        logger.info("🌐 You can now start the API server with: uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Insurance Claims Data Automation System")
    print("=" * 50)
    
    # Run initialization
    success = asyncio.run(initialize_system())
    
    if success:
        print("\n✅ System ready!")
        print("\n📋 Next steps:")
        print("1. Start the API server: uvicorn app.main:app --reload")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Upload data: POST /upload-data")
        print("4. Generate reports: GET /api/v1/dashboard/excel")
        print("\n🐳 Or run with Docker: docker-compose up")
    else:
        print("\n❌ System initialization failed!")
        print("Please check the logs and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

