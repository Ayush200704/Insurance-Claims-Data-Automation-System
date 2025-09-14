"""
Database configuration and models
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
from loguru import logger

from app.core.config import settings

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InsuranceClaim(Base):
    """Insurance claims data model"""
    __tablename__ = "insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    sex = Column(Integer, nullable=False)  # 0 for female, 1 for male
    bmi = Column(Float, nullable=False)
    children = Column(Integer, nullable=False)
    smoker = Column(Integer, nullable=False)  # 0 for no, 1 for yes
    region = Column(Integer, nullable=False)  # 0-3 for different regions
    charges = Column(Float, nullable=False)
    insuranceclaim = Column(Integer, nullable=False)  # 0 for no claim, 1 for claim
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReserveCalculation(Base):
    """Reserve calculation results"""
    __tablename__ = "reserve_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    method = Column(String(50), nullable=False)
    total_reserves = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    parameters = Column(Text)  # JSON string of calculation parameters
    created_at = Column(DateTime, default=datetime.utcnow)


class TrendAnalysis(Base):
    """Trend analysis results"""
    __tablename__ = "trend_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    metric = Column(String(50), nullable=False)
    trend_direction = Column(String(20), nullable=False)
    trend_strength = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    confidence_interval = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_data_to_db(file_path: str):
    """Load insurance claims data from CSV to database"""
    try:
        # Read CSV data
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Insert data into database
        df.to_sql('insurance_claims', engine, if_exists='append', index=False)
        logger.info(f"Successfully loaded {len(df)} records to database")
        
        return len(df)
        
    except Exception as e:
        logger.error(f"Error loading data to database: {e}")
        raise


def get_claims_data() -> pd.DataFrame:
    """Retrieve claims data from database"""
    try:
        query = "SELECT * FROM insurance_claims"
        df = pd.read_sql(query, engine)
        logger.info(f"Retrieved {len(df)} claims records from database")
        return df
    except Exception as e:
        logger.error(f"Error retrieving claims data: {e}")
        raise